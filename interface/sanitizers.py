class Sanitizer:
    
    @classmethod
    def clean_name(cls, name: str) -> str:
        name = ' '.join([part.strip() for part in name.split()])
        name = name.lower().title()
        return name
    
    @classmethod
    def get_names(cls, name: str) -> tuple[str, str]:
        name = cls.clean_name(name) 
        return name.split()[0], ' '.join(name.split()[1:])