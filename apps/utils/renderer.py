from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response


class ApiRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        resp: Response = renderer_context.get("response")

        response_dict = {
            "message": resp.status_text,
            "status": resp.status_code,
            "data": data,
        }
        if resp.status_code >= 400:
            response_dict["message"] = (
                data.get("detail")
                if isinstance(data, dict)
                else [str(i) for i in data]
            )
            del response_dict["data"]
        else:
            if isinstance(data, dict):
                response_dict["data"] = data.get("data") or data
                response_dict["message"] = (
                    data.get("message") or response_dict["message"]
                )
        data = response_dict
        return super().render(data, accepted_media_type, renderer_context)
