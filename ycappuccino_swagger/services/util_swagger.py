"""
utilities that allow to generate swagger.json
"""
from pelix.ipopo.decorators import Instantiate, Requires, Provides, ComponentFactory, Property, BindField, UnbindField

from ycappuccino_api.core.api import IActivityLogger
from ycappuccino_core.decorator_app import map_app_class, Layer
from ycappuccino_api.endpoints.api import IHandlerEndpoint
from ycappuccino_endpoints.beans import EndpointResponse


@ComponentFactory('UtilSwagger-Factory')
@Provides(specifications=[IHandlerEndpoint.name])
@Requires("_log", IActivityLogger.name, spec_filter="'(name=main)'")
@Property('_name', "name", "swagger")
@Instantiate("UtilSwagger")
@Requires("_handler_endpoints", specification=IHandlerEndpoint.name, aggregate=True, optional=True)
@Layer(name="ycappuccino_swagger")
class UtilSwagger(IHandlerEndpoint):

    def __init__(self):
        super(IHandlerEndpoint, self).__init__();
        self._handler_endpoints = None
        self._map_handler_endpoints = {}

    def get_types(self):
        return ["swagger"]

    @BindField("_handler_endpoints")
    def bind_manager(self, field, a_handler_endpoint, a_service_reference):
        w_item_plurals = a_handler_endpoint.get_types()
        for w_item_plural in w_item_plurals:
            self._map_handler_endpoints[w_item_plural] = a_handler_endpoint

    @UnbindField("_handler_endpoints")
    def unbind_manager(self, field, a_handler_endpoint, a_service_reference):
        w_item_plurals = a_handler_endpoint.get_types()
        for w_item_plural in w_item_plurals:
            self._map_handler_endpoints[w_item_plural] = None

    def post(self,  a_path, a_headers, a_body):
        pass

    def put(self, a_path, a_headers, a_body):
        pass

    def get(self, a_path, a_headers):
        w_path = {}
        w_tag = []

        w_scheme = ["https","http"]
        w_swagger = {
            "swagger": "2.0",
            "info": {},
            "basePath": "/api/",
            "tags": w_tag,
            "schemes": w_scheme,
            "paths": w_path
        }
        for w_handle_endpoints in self._map_handler_endpoints.values():
            if "swagger" not in w_handle_endpoints.get_types():
                w_handle_endpoints.get_swagger_descriptions(w_tag, w_swagger, w_scheme)

        return EndpointResponse(200, None, None, w_swagger)

    def delete(self, a_path, a_headers):
        pass

    def get_swagger_description_tag(self,  a_item):
        return map_app_class[a_item["_class"]] + " - " + a_item["plural"]


    def get_swagger_description_service_tag(self,  a_service):
        return "$service " + a_service.get_name()


    def get_swagger_description_path(self,  a_item, a_with_id):
        """ query can be get, getAll, put, post and delete """
        w_path = "/$crud/" + a_item["plural"]
        if a_with_id:
            w_path = w_path + "/{id}"
        return w_path


    def get_swagger_description_empty(self,  a_item, a_path):
        """ return the path description for the item"""
        a_path["/$empty/" + a_item["plural"]] = {
            "get": {
                "tags": [self.get_swagger_description_tag(a_item)],
                "operationId": "empty_" + a_item["plural"],
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [],
                "responses": {
                    "default": {
                        "description": "successful operation"
                    }
                }
            }
        }


    def get_swagger_description_schema( self, a_item, a_path):
        """ return the path description for the item"""
        a_path["/$schema/" + a_item["plural"] ] = {
            "get": {
                "tags": [self.get_swagger_description_tag(a_item)],
                "operationId": "schema_" + a_item["plural"],
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [],
                "responses": {
                    "default": {
                        "description": "successful operation"
                    }
                }
            }
        }
        if a_item["multipart"] :
            a_path["/$multipart/" + a_item["plural"] ] = {
                "get": {
                    "tags": [self.get_swagger_description_tag(a_item)],
                    "operationId": "multipart_" + a_item["plural"],
                    "consumes": ["application/json"],
                    "produces": ["application/json"],
                    "parameters": [],
                    "responses": {
                        "default": {
                            "description": "successful operation"
                        }
                    }
                }
            }



    def get_params(self, a_path):
        w_params = []

        w_path_param = a_path
        if "?" in a_path:
            w_path_param = a_path[0:a_path.indexOf("?")]
        if "/" in w_path_param:
            w_path_params = w_path_param.split("/")
            for w_elem in w_path_params:
                if w_elem[0] == "{" and w_elem[-1] == "}":
                    w_params.append({
                        "name": w_elem[1:-1],
                        "required": True,
                        "in": "path",
                        "type": "string"
                    })
        return w_params

    def get_query_params(self, a_path):
        w_params = []

        if "?" in a_path:
            w_path_param = a_path[0:a_path.indexOf("?")]
            w_query = a_path[a_path.indexOf("?") + 1]
            w_querys = []
            if "&" in w_query:
                w_querys = w_query.split("&")
            else:
                w_querys = [w_query]
            for w_elem in w_querys:
                if w_elem[0] == "{" and w_elem[-1] == "}":
                    w_params.append({
                        "in": "query",
                        "name": w_elem[1:-2],
                        "required": True,
                        "type": "string"

                    })
        return w_params

    def get_swagger_description_service(self,  a_service, a_path):
        """ return the path description for the item"""

        a_path["/$service/" + a_service.get_name()] = {}
        w_extra_path = a_service.get_extra_path()
        if a_service.has_post():
            if a_service.has_root_path():
                a_path["/$service/" + a_service.get_name()]["post"] = {
                    "tags": [self.get_swagger_description_service_tag(a_service)],
                    "operationId": "post_service_" + a_service.get_name(),
                    "consumes": ["application/json"],
                    "produces": ["application/json"],
                    "parameters": [{
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    }],
                    "responses": {
                        "default": {
                            "description": "successful operation"
                        }
                    }
                }
            if "post" in w_extra_path.keys():
                for w_path in w_extra_path["post"]:
                    w_params = self.get_params(w_path)
                    w_query_params = self.get_query_params(w_path)

                    if not "/$service/" + a_service.get_name() + "/" + w_path in a_path.keys():
                        a_path["/$service/" + a_service.get_name() + "/" + w_path] = {}

                    a_path["/$service/" + a_service.get_name()+"/"+w_path]["post"] = {
                        "tags": [self.get_swagger_description_service_tag(a_service)],
                        "operationId": "post_service_" + a_service.get_name()+"/"+w_path,
                        "consumes": ["application/json"],
                        "produces": ["application/json"],
                        "parameters": w_params,
                        "responses": {
                            "default": {
                                "description": "successful operation"
                            }
                        }
                    }

        if a_service.has_put():
            if a_service.has_root_path():

                a_path["/$service/" + a_service.get_name()]["put"] = {
                    "tags": [self.get_swagger_description_service_tag(a_service)],
                    "operationId": "put_service_" + a_service.get_name(),
                    "consumes": ["application/json"],
                    "produces": ["application/json"],
                    "parameters": [{
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    }],
                    "responses": {
                        "default": {
                            "description": "successful operation"
                        }
                    }
                }
            if "put" in w_extra_path.keys():
                for w_path in w_extra_path["put"]:
                    w_params = self.get_params(w_path)
                    w_query_params = self.get_query_params(w_path)
                    if not "/$service/" + a_service.get_name() + "/" + w_path in a_path.keys():
                        a_path["/$service/" + a_service.get_name() + "/" + w_path] = {}

                    a_path["/$service/" + a_service.get_name() + "/" + w_path]["put"] = {
                        "tags": [self.get_swagger_description_service_tag(a_service)],
                        "operationId": "put_service_" + a_service.get_name() + "/" + w_path,
                        "consumes": ["application/json"],
                        "produces": ["application/json"],
                        "parameters": w_params,
                        "responses": {
                            "default": {
                                "description": "successful operation"
                            }
                        }
                    }

        if a_service.has_get():
            if a_service.has_root_path():

                a_path["/$service/" + a_service.get_name()]["get"] = {
                    "tags": [self.get_swagger_description_service_tag(a_service)],
                    "operationId": "get_service_" + a_service.get_name(),
                    "consumes": ["application/json"],
                    "produces": ["application/json"],
                    "parameters": [],
                    "responses": {
                        "default": {
                            "description": "successful operation"
                        }
                    }
                }
            if "get" in w_extra_path.keys():

                for w_path in w_extra_path["get"]:
                    w_params = self.get_params(w_path)
                    w_query_params = self.get_query_params(w_path)
                    if not "/$service/" + a_service.get_name() + "/" + w_path in a_path.keys():
                        a_path["/$service/" + a_service.get_name() + "/" + w_path] = {}
                    a_path["/$service/" + a_service.get_name() + "/" + w_path]["get"] = {
                        "tags": [self.get_swagger_description_service_tag(a_service)],
                        "operationId": "get_service_" + a_service.get_name() + "/" + w_path,
                        "consumes": ["application/json"],
                        "produces": ["application/json"],
                        "parameters": w_params,
                        "responses": {
                            "default": {
                                "description": "successful operation"
                            }
                        }
                    }
        if a_service.has_delete():
            if a_service.has_root_path():

                a_path["/$service/" + a_service.get_name()]["delete"] = {
                    "tags": [self.get_swagger_description_service_tag(a_service)],
                    "operationId": "delete_service_" + a_service.get_name(),
                    "consumes": ["application/json"],
                    "produces": ["application/json"],
                    "parameters": [],
                    "responses": {
                        "default": {
                            "description": "successful operation"
                        }
                    }
                }
            if "delete" in w_extra_path.keys():
                for w_path in w_extra_path["delete"]:
                    w_params = self.get_params(w_path)
                    w_query_params = self.get_query_params(w_path)
                    if not "/$service/" + a_service.get_name() + "/" + w_path in a_path.keys():
                        a_path["/$service/" + a_service.get_name() + "/" + w_path]= {}
                    a_path["/$service/" + a_service.get_name() + "/" + w_path]["delete"] = {
                        "tags": [self.get_swagger_description_service_tag(a_service)],
                        "operationId": "delete_service_" + a_service.get_name() + "/" + w_path,
                        "consumes": ["application/json"],
                        "produces": ["application/json"],
                        "parameters": w_params,
                        "responses": {
                            "default": {
                                "description": "successful operation"
                            }
                        }
                    }

        return a_path


    def get_swagger_description(self,  a_item, a_path):
        """ return the path description for the item"""
        a_path[self.get_swagger_description_path(a_item, False)] = {
            "get": {
                "tags": [self.get_swagger_description_tag(a_item)],
                "operationId": "getAll_" + a_item["id"],
                "produces": ["application/json"],
                "parameters": [{
                    "name": "filter",
                    "in": "query",
                    "required": False,
                    "type": "string"
                }, {
                    "name": "offset",
                    "in": "query",
                    "required": False,
                    "type": "integer",
                    "default": 0,
                    "format": "int32"
                }, {
                    "name": "limit",
                    "in": "query",
                    "required": False,
                    "type": "integer",
                    "default": 50,
                    "format": "int32"
                }, {
                    "name": "expand",
                    "in": "query",
                    "required": False,
                    "type": "string"
                }, {
                    "name": "sort",
                    "in": "query",
                    "required": False,
                    "type": "string"
                }],
                "responses": {
                    "default": {
                        "description": "successful operation"
                    }
                }
            }
        }
        if a_item["isWritable"]:
            a_path[self.get_swagger_description_path(a_item, False)]["post"] = {
                "tags": [self.get_swagger_description_tag(a_item)],
                "operationId": "create_" + a_item["id"],
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [{
                    "in": "body",
                    "name": "body",
                    "required": True,
                    "schema": {
                        "type": "string"
                    }
                }],
                "responses": {
                    "default": {
                        "description": "successful operation"
                    }
                }
            }

        if a_item["multipart"] :
            a_path[self.get_swagger_description_path(a_item, False)+"/blob"] = {
                "post": {
                    "tags": [self.get_swagger_description_tag(a_item)+"/blob"],
                    "operationId": "createBlob_" + a_item["id"],
                    "consumes": ["multipart/form-data"],
                    "produces": ["application/json"],
                    "parameters": [{
                        "in": "body",
                        "name": "attachmentType",
                        "description": "The attachment type.",
                        "required": False,
                        "schema": {
                            "type": "string"
                        }
                    }, {
                        "in": "body",
                        "name": "attachmentName",
                        "description": "The attachment type.",
                        "required": False,
                        "schema": {
                            "type": "string"
                        }
                    }],
                    "responses": {
                        "default": {
                            "description": "successful operation"
                        }
                    }
                }
            }
            a_path[self.get_swagger_description_path(a_item, False) + "/blob/base64"] = {
                "post": {
                    "tags": [self.get_swagger_description_tag(a_item) + "/blob/base64"],
                    "operationId": "createBlob64_" + a_item["id"],
                    "consumes": ["application/json"],
                    "produces": ["application/json"],
                    "parameters": [{
                        "in": "body",
                        "name": "file",
                        "description": "file in base 64 and file name, extention etc",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    }],
                    "responses": {
                        "default": {
                            "description": "successful operation"
                        }
                    }
                }
            }
        a_path[self.get_swagger_description_path(a_item, True)] = {
            "get": {
                "tags": [self.get_swagger_description_tag(a_item)],
                "operationId": "getItem_" + a_item["id"],
                "produces": ["application/json"],
                "parameters": [{
                    "name": "id",
                    "in": "path",
                    "required": True,
                    "type": "string"
                }, {
                    "name": "expand",
                    "in": "query",
                    "required": False,
                    "type": "string"
                }],
                "responses": {
                    "default": {
                        "description": "successful operation"
                    }
                }
            }
        }
        if a_item["isWritable"]:
            a_path[self.get_swagger_description_path(a_item, False)]["put"] = {
                "tags": [self.get_swagger_description_tag(a_item)],
                "operationId": "update_" + a_item["id"],
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [{
                    "in": "body",
                    "name": "body",
                    "required": True,
                    "schema": {
                        "type": "string"
                    }
                }, {
                    "name": "id",
                    "in": "path",
                    "required": True,
                    "type": "string"
                }],
                "responses": {
                    "default": {
                        "description": "successful operation"
                    }
                }
            }

        self.get_swagger_description_empty(a_item, a_path)
        self.get_swagger_description_schema(a_item, a_path)

        return a_path


    def get_swagger_description_item(self,  a_path):
        """ return the path description for the item"""
        a_path["/$crud/items"] = {
            "get": {
                "tags": ["Core : Items"],
                "operationId": "getAll_Item",
                "produces": ["application/json"],
                "parameters": [],
                "responses": {
                    "default": {
                        "description": "successful operation"
                    }
                }
            }
        }
        a_path["/$crud/items/{id}"] = {
            "get": {
                "tags": ["Core : Items"],
                "operationId": "getItem_item",
                "produces": ["application/json"],
                "parameters": [{
                    "name": "id",
                    "in": "path",
                    "required": True,
                    "type": "string"
                }],
                "responses": {
                    "default": {
                        "description": "successful operation"
                    }
                }
            }
        }

        return a_path




