"""
IHost swagger component that provide swagger api
"""

from ycappuccino_api.core import IActivityLogger
from ycappuccino_api.host import IHost

import logging, os
from pelix.ipopo.decorators import (
    ComponentFactory,
    Requires,
    Validate,
    Invalidate,
    Provides,
    Instantiate,
)


import inspect
import base64

from ycappuccino.api.proxy import YCappuccinoRemote
from ycappuccino.core.decorator_app import Layer

_logger = logging.getLogger(__name__)


@ComponentFactory("HostSwagger-Factory")
@Provides(specifications=[YCappuccinoRemote.__name__, IHost.__name__])
@Requires("_log", IActivityLogger.__name__, spec_filter="'(name=main)'")
@Instantiate("HostSwagger")
@Layer(name="ycappuccino_swagger")
class HostSwagger(IHost):

    def __init__(self):
        super(IHost, self).__init__()
        self.path_core = inspect.getmodule(self).__file__.replace(
            "services{0}swagger.py".format(os.path.sep), ""
        )
        self._log = None
        self._secure = False
        self._user = None
        self._pass = None
        self._id = "/swagger"
        self._priority = 0
        self._subpath = "swagger"
        self._config = None

    def get_path(self):
        w_path = [self.path_core + self._subpath]

        return w_path

    def get_ui_path(self):
        return self._id

    def get_priority(self):
        return self._priority

    def get_subpath(self):
        return self._subpath

    def is_auth(self):
        return self._secure

    def get_id(self):
        return self._id

    def get_type(self):
        return "swagger"

    def is_core(self):
        return True

    def load_configuration(self):
        if self._secure:
            self._user = self._config.get(self._id + ".login", "client_pyscript_core")
            self._pass = self._config.get(self._id + ".password", "1234")

    def check_auth(self, a_authorization):
        if a_authorization is not None and "Basic " in a_authorization:
            w_decode = base64.standard_b64decode(
                a_authorization.replace("Basic ", "")
            ).decode("ascii")
            if ":" in w_decode:
                w_user = w_decode.split(":")[0]
                w_pass = w_decode.split(":")[1]
                if w_user == self._user and w_pass == self._pass:
                    return True

        return False

    @Validate
    def validate(self, context):
        self._log.info("HostSwagger validating")
        self.load_configuration()

        self._log.info("HostSwagger validated")

    @Invalidate
    def invalidate(self, context):
        self._log.info("HostSwagger invalidating")

        self._log.info("HostSwagger invalidated")
