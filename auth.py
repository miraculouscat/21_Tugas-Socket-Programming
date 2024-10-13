class AuthManager:
    def __init__(self):
        self.users = {}

    def register(self, username, password):
        if username in self.users:
            return False, "Username already taken."
        self.users[username] = password
        return True, "Registration successful."

    def login(self, username, password):
        if username in self.users and self.users[username] == password:
            return True, "Login successful."
        return False, "Invalid username or password."
