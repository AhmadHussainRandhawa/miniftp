<div align="center">

# MiniFTP

**A custom file transfer system, built from scratch in Python.**

No FTP libraries. No web framework. Just TCP sockets, a custom application-layer protocol, authenticated sessions, a virtual filesystem, and binary file transfer — implemented by hand.

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white">
  <img alt="Protocol" src="https://img.shields.io/badge/Protocol-Custom%20TCP-blue">
  <img alt="Transport" src="https://img.shields.io/badge/Transport-TCP-success">
  <img alt="Dependencies" src="https://img.shields.io/badge/Dependencies-Zero-brightgreen">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-yellow">
</p>

</div>

---

## 🎬 See it in action

https://github.com/user-attachments/assets/75238e31-93b9-484c-9a33-6ad9e85637e7

*Live run: TCP connection → authentication → virtual filesystem navigation → file download → binary file upload → graceful logout.*

---

## 📑 Contents

- [What is MiniFTP?](#what-is-miniftp)
- [Getting Started](#getting-started)
- [Features](#features)
- [Protocol](#protocol)
- [File Transfer](#file-transfer)
- [Path Traversal Protection](#path-traversal-protection)
- [Configuration](#configuration)
- [Supported Commands](#supported-commands)
- [Architecture](#architecture)
- [Known Limitations](#known-limitations)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

<a id="what-is-miniftp"></a>
## ✨ What is MiniFTP?

MiniFTP is a small client-server file transfer system built directly on top of TCP sockets. It implements its own application-layer protocol for commands, responses, authentication, filesystem navigation, and file transfer — without relying on an existing FTP implementation.

The project is being developed incrementally, release by release. The current release is **v0.5 — File Transfer**. See the [Roadmap](#roadmap) below for what's done and what's next.

---

<a id="getting-started"></a>
## Getting Started

### Requirements

* Python **3.12+** *(nested-quote f-strings in `server.py` require PEP 701; developed on 3.14)*
* No third-party dependencies — standard library only

### Run it

```bash
git clone git@github.com:AhmadHussainRandhawa/miniftp.git
cd miniftp

# terminal 1
python3 server.py

# terminal 2
python3 client.py
```

<details>
<summary><strong>Full sample session</strong> (click to expand)</summary>

```text
> LOGIN ahmad 1234
Server: OK Welcome ahmad

> PWD
Server: OK /

> CD /downloads
Server: OK Current directory: /downloads

> LS
Server: OK ['book.pdf', 'layout.html']

> GET book.pdf
Server: OK 5230258
Received 5230258/5230258 bytes
Download complete: .../client_downloads/book.pdf

> PUT image123.jpg
Server: OK READY
Server: OK SEND FILE
Sent 1006785/1006785 bytes
Upload complete: image123.jpg

> QUIT
Server: OK Goodbye
Connection closed.
```

</details>

---

<a id="features"></a>
## ⚡ Features

| Layer | Capabilities |
| :--- | :--- |
| **Networking** | Persistent TCP connections, raw sockets, line-delimited messages, graceful shutdown |
| **Protocol** | Custom application-layer protocol, request parsing, command dispatch, structured `OK`/`ERROR` responses |
| **Authentication** | Username/password login, per-client session state, auth-gated commands |
| **Virtual Filesystem** | Sandboxed storage root, `PWD`/`CD`/`LS`, path normalization, traversal protection |
| **File Transfer** | `GET`/`PUT`, binary-safe chunked streaming, exact size tracking, progress reporting |

---

<a id="protocol"></a>
## 📡 Protocol

Commands are newline-terminated text; responses follow a consistent `OK`/`ERROR` format:

```text
LOGIN ahmad 1234
→ OK Welcome ahmad
```

<details>
<summary><strong>Protocol pipeline diagram</strong> (click to expand)</summary>

```text
Client message
      │
      ▼
   Parser
      │
      ▼
Command + Arguments
      │
      ▼
  Dispatcher
      │
      ▼
Command Handler
      │
      ▼
Protocol Response
```

Parsing is fully separate from command behavior, which keeps adding new commands straightforward.

</details>

---

<a id="file-transfer"></a>
## 📁 File Transfer

File transfer is a separate phase from command exchange. **`GET`**: the server announces the byte count first (`OK <size>`), then streams exactly that many bytes — necessary because TCP is a byte stream with no built-in message boundaries. **`PUT`**: the client and server negotiate readiness (`OK READY` → size → `OK SEND FILE`) before the binary payload starts. Both directions stream in fixed-size chunks rather than loading the whole file into memory.

<details>
<summary><strong>Sequence diagrams</strong> (click to expand)</summary>

**Download — `GET`**
```text
Client                         Server
  │──── GET book.pdf ───────────►│
  │◄──── OK 5230258 ─────────────│
  │◄──── binary data ────────────│
  │◄────────── ... ──────────────│
```

**Upload — `PUT`**
```text
Client                         Server
  │──── PUT image.jpg ──────────►│
  │◄──── OK READY ───────────────│
  │──── 1006785 ────────────────►│
  │◄──── OK SEND FILE ───────────│
  │──── binary data ────────────►│
  │─────── ... ─────────────────►│
```

</details>

---

<a id="path-traversal-protection"></a>
## 🔒 Path Traversal Protection

Every client-supplied path passes two independent checks before touching the real filesystem: **(1)** `.`/`..` segments are normalized in pure path arithmetic against the client's virtual directory — no filesystem access yet; **(2)** the resulting path is resolved against the real storage root and verified to still be a descendant of it, via `Path.resolve()` + containment check. Anything that would escape raises `PathTraversalError` and is rejected. A client can never reach outside the configured `storage/` directory.

---

<a id="configuration"></a>
## ⚙️ Configuration

All runtime settings live in `config.py`:

| Setting | Default | Description |
| :--- | :--- | :--- |
| `HOST` | `127.0.0.1` | Server bind address |
| `PORT` | `2121` | Server listening port |
| `BUFFER_SIZE` | `4096` | Chunk size (bytes) for streaming transfers |
| `STORAGE_ROOT` | `./storage` | Sandboxed root for all file operations |

---

<a id="supported-commands"></a>
## 🧭 Supported Commands

| Command | Description | Auth required |
| :--- | :--- | :--: |
| `PING` | Test connectivity | No |
| `INFO` | Server and session info | No |
| `HELP` | List supported commands | No |
| `LOGIN` | Authenticate | No |
| `LOGOUT` | End session | No |
| `PWD` | Show current directory | Yes |
| `CD` | Change directory | Yes |
| `LS` | List directory contents | Yes |
| `GET` | Download a file | Yes |
| `PUT` | Upload a file | Yes |
| `QUIT` | Close connection | No |

---

<a id="architecture"></a>
## 🏗️ Architecture

| Module | Responsibility |
| :--- | :--- |
| `server.py` | TCP server, connection lifecycle |
| `client.py` | Interactive client, file transfers |
| `protocol.py` | Message parsing, command dispatch |
| `commands/handlers.py` | Command implementations |
| `session.py` | Authentication and transfer state |
| `virtual_fs.py` | Virtual paths, filesystem access |
| `auth.py` | User authentication |
| `config.py` | Runtime configuration |
| `exceptions.py` | Filesystem-related exceptions |

<details>
<summary><strong>Component diagram</strong> (click to expand)</summary>

```text
                         ┌─────────────────┐
                         │     Client      │
                         │    client.py    │
                         └────────┬────────┘
                                  │ TCP
                                  ▼
                         ┌─────────────────┐
                         │     Server      │
                         │    server.py    │
                         └────────┬────────┘
                                  ▼
                         ┌─────────────────┐
                         │    Protocol     │
                         │   protocol.py   │
                         └────────┬────────┘
                                  ▼
                         ┌─────────────────┐
                         │    Commands     │
                         │    handlers.py  │
                         └───────┬─────────┘
                       ┌─────────┴─────────┐
                       ▼                   ▼
              ┌────────────────┐  ┌────────────────┐
              │    Session     │  │  Virtual FS    │
              │   session.py   │  │ virtual_fs.py  │
              └────────────────┘  └───────┬────────┘
                                          ▼
                                  ┌────────────────┐
                                  │    Storage     │
                                  │    storage/    │
                                  └────────────────┘
```

</details>

---

<a id="known-limitations"></a>
## ⚠️ Known Limitations

Disclosed here rather than left for someone to discover:

* **Passwords are stored and compared in plaintext**, not hashed. Hashing (`bcrypt`/`argon2`) is a priority fix planned ahead of any production-facing use — don't reuse a real password with this project.
* **Single client at a time** — the accept loop handles one connection per iteration; a second client blocks until the first disconnects. Fixed alongside the control/data connection split in v0.6–v0.7.
* **No passive-mode/dual-connection architecture yet** — control and data share one TCP connection, unlike standard FTP. Planned for v0.6–v0.7.
* **No role-based permissions yet** — any authenticated user has full read/write access. Planned for v0.8.

---

<a id="roadmap"></a>
## 🛣️ Roadmap

| Release | Milestone | Status |
| :--: | :--- | :--: |
| `v0.1` | Communication Foundation | ✅ |
| `v0.2` | Protocol Foundation | ✅ |
| `v0.3` | Session & Authentication | ✅ |
| `v0.4` | Virtual Filesystem | ✅ |
| `v0.5` | File Transfer | ✅ |
| `v0.6` | FTP Architecture | Planned |
| `v0.7` | Passive Mode | Planned |
| `v0.8` | Authorization & Permissions | Planned |
| `v0.9` | Reliability & Engineering | Planned |
| `v1.0` | Production-Quality MiniFTP | Planned |

<details>
<summary><strong>What's next, in detail</strong> (click to expand)</summary>

**v0.6 — FTP Architecture**: FTP-style control and data connections, connection coordination, transfer lifecycle management.

**v0.7 — Passive Mode**: Dynamic data ports, passive-mode negotiation, multiple concurrent transfers.

**v0.8 — Authorization & Permissions**: Read/write/delete permissions, role-based access control.

**v0.9 — Reliability & Engineering**: Structured logging, timeouts, config hardening, error handling, recovery, and moving off plaintext passwords.

**v1.0 — Production-Quality MiniFTP**: Polished client/server, full documentation, install guide, example workflows.

</details>

---

<a id="contributing"></a>
## 🤝 Contributing

MiniFTP is being built in public, one scoped release at a time — and contributions are genuinely welcome, not just tolerated. Useful ways to get involved:

- **Try the roadmap** — pick an item from [v0.6 onward](#roadmap) and open a PR; the architecture is small enough to be approachable
- **Report bugs or security gaps** — especially anything beyond what's already listed in [Known Limitations](#known-limitations)
- **Test on your setup** — different OS, different Python 3.12+ versions, and report what breaks
- **Improve the docs** — clarify anything in this README that wasn't obvious on first read

If MiniFTP is useful to you or you're following along with its development, **a ⭐ on the repo genuinely helps others find it.**

---

<a id="license"></a>
## License

Licensed under the [MIT License](./LICENSE).