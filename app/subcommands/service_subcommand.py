import functools
import os
import sys
import tornado.ioloop

from app.subcommands.subcommand import Subcommand
from app.util.fs import write_file
from app.util.unhandled_exception_handler import UnhandledExceptionHandler


class ServiceSubcommand(Subcommand):
    """
    Base class for Master and Slave subcommands.
    """
    def _start_application(self, application, port):
        # Note: No significant application logic should be executed before this point. The call to application.listen()
        # will raise an exception if another process is using the same port. We rely on this exception to force us to
        # exit if there are any port conflicts.
        try:
            application.listen(port, '0.0.0.0')
        except OSError:
            self._logger.error('Could not start application on port {}. Is port already in use?'.format(port))
            sys.exit(1)

        ioloop = tornado.ioloop.IOLoop.instance()

        # add a teardown callback that will stop the tornado server
        stop_tornado_ioloop = functools.partial(ioloop.add_callback, callback=ioloop.stop)
        UnhandledExceptionHandler.singleton().add_teardown_callback(stop_tornado_ioloop)
        return ioloop

    def _write_pid_file(self, filename):
        write_file(str(os.getpid()), filename)

        def remove_pid_file():
            try:
                os.remove(filename)
            except OSError:
                pass
        UnhandledExceptionHandler.singleton().add_teardown_callback(remove_pid_file)
