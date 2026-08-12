from auth import authenticate
from config import SERVER_NAME, SERVER_VERSION
from virtual_fs import VirtualFileSystem
from exceptions import PathTraversalError, DirectoryNotFoundError


vfs = VirtualFileSystem()


SUPPORTED_COMMANDS = {
    "PING",
    "HELP",
    "INFO",
    "QUIT",
    "LOGIN",
    "PWD",
    "LOGOUT",
    "CD",
    "LS",
    "GET",
    "PUT",
}


def ok(message: str) -> dict:
    return {
        "status": 'OK',
        "message": message,
    }


def error(message: str) -> dict:
    return {
        "status": 'ERROR',
        "message": message,
    }


def handle_ping(arguments: list[str], session) -> dict:
    return ok("PONG")


def handle_info(arguments: list[str], session) -> dict:
    username = session.username or "Anonymous"

    authenticated = "Yes" if session.is_authenticated() else "No"
    

    message = (
        f"{SERVER_NAME} v{SERVER_VERSION}"
        f"User: {username}"
        f"Authenticated: {authenticated}"
    )

    return ok(message)


def handle_help(arguments: list[str], session) -> dict: 
    commands = ", ".join(sorted(SUPPORTED_COMMANDS))
    return ok(f"Supported commands {commands}")


def handle_quit(arguments: list[str], session) -> dict:
    return ok("Goodbye")


def handle_login(arguments: list[str], session) -> dict:
    if len(arguments) != 2:
        return error("Usage: LOGIN <username> <password>")

    username, password = arguments

    if not authenticate(username, password):
        return error("Invalid username or password.")

    session.login(username)

    return ok(f"Welcome {username}")


def handle_logout(arguments, session):
    if not session.is_authenticated():
        return error("You are not logged in")
    
    username = session.username

    session.logout()

    return ok(f"Goodbye {username}")


def handle_pwd(argumnets, session):
    if argumnets:
        return error("usage <PWD>")

    return ok(str(session.current_directory))


def handle_cd(arguments, session):
    if len(arguments) != 1:
        return error("Usage: CD <directory>")
    
    target = arguments[0]

    try: 
        virtual_path = vfs.resolve_virtual_path(session.current_directory, target)

        vfs.directory_exists(virtual_path)

    except PathTraversalError:
        return error("Access denied.")
    
    except DirectoryNotFoundError:
        return error("Directory does not exists.")

    session.current_directory = virtual_path

    return ok(f"Current directory: {virtual_path}")


def handle_ls(arguments, session):
    if arguments:
        return error("Usage: LS")
    
    entries = vfs.list_directory(session.current_directory)
    
    if not entries:
        return error("Directory is empty")
    
    return ok((entries))


def handle_get(arguments, session):
    if len(arguments) != 1:
        return error("Usage GET <filename>")

    target = arguments[0]    
    virtual_path = vfs.resolve_virtual_path(session.current_directory, target)

    if not vfs.file_exists(virtual_path):
        return error("File does not exists.")

    session.start_download(virtual_path)

    size = vfs.get_file_size(virtual_path)

    return ok(str(size))


def handle_put(arguments, session):
    if len(arguments) != 1:
        return error('Usage PUT <filename>')
    
    target = arguments[0]

    virtual_path = vfs.resolve_virtual_path(session.current_directory, target)

    session.start_upload(virtual_path)
    
    return ok("READY")
    

