
class Message:
    def __init__(self="", author_name="", text="",
                 is_mod=False, is_owner=False) -> None:
        self.author_name = author_name
        self.text = text
        self.is_mod = is_mod
        self.is_owner = is_owner

    # getters
    def get_author_name(self) -> None:
        return self.author_name

    def get_is_mod(self) -> None:
        return self._is_mod

    def get_is_owner(self) -> None:
        return self._is_owner

    def get_text(self) -> None:
        return self._text

    # setters
    def set_author_name(self, item) -> None:
        self.author_name = item["authorDetails"]["displayName"]

    def load_msg(self, item) -> None:
        self.set_text(item)
        self.set_author_name(item)
        self.set_is_mod(item)
        self.set_is_owner(item)

    def set_is_mod(self, item) -> None:
        self.is_mod = item["authorDetails"]["isChatModerator"]

    def set_is_owner(self, item) -> None:
        self.is_owner = item["authorDetails"]["isChatOwner"]

    def set_text(self, item) -> None:
        self.text = item["snippet"]["displayMessage"]
