import abc


class Service:

    @abc.abstractmethod
    def execute(self, queryset):
        pass
