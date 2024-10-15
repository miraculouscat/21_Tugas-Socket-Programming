class AuthManager:
    def __init__(self):
        self.users = {}

    def register(self, username, password):
        print(f"Attempting to register: {username}")
        if username in self.users:
            print(f"Registration failed: {username} already taken.")
            return False, "Username already taken."
        self.users[username] = password
        print(f"Registration successful: {username} registered.")
        return True, "Registration successful."

    def login(self, username, password):
        if username not in self.users:
            return False, "Username does not exist."
        if self.users[username] == password:
            return True, "Login successful."
        return False, "Invalid username or password."
