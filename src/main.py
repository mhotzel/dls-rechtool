from application.application_context import ApplicationContext
from application.event_dispatcher import AppEvent


if __name__ == '__main__':
    appContext = ApplicationContext()
    appContext.run()
