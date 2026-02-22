# app/middleware/engine.py

 #from app.middleware.base import MiddlewareException
#from app.services.event_logger import log_event
#from app.services.run_registry import update_status


#class MiddlewareEngine:
#    def __init__(self, middlewares: list):
 ### def run(self, context: dict) -> dict:
    #    for middleware in self.middlewares:
     #       try:
       #         context = middleware.process(context)

      #          log_event(
        #            run_id=context["run_id"],
         #           node_name=middleware.name,
          #          event_type="MIDDLEWARE",
           #         summary="Executed successfully"
            #    )
#
 #               # ✅ ESCALATE persistence fix
  #              if context.get("terminal_status") == "ESCALATE":
   #                 update_status(context["run_id"], "ESCALATED")
    #                return context
#
 #           except MiddlewareException as e:
  #              context["terminal_status"] = "FAILED"

#                update_status(context["run_id"], "FAILED")

 #               log_event(
  #                  run_id=context["run_id"],
   #                 node_name=middleware.name,
    #                event_type="ERROR",
     #               summary=str(e)
      #          )
#
 #               return context
#
 #       return context

# app/middleware/engine.py

from app.middleware.base import MiddlewareException
from app.services.event_logger import log_event
from app.services.run_registry import update_status


class MiddlewareEngine:
    def __init__(self, middlewares: list):
        self.middlewares = middlewares

    def run(self, context: dict) -> dict:
        run_id = context["run_id"]

        for middleware in self.middlewares:
            try:
                context = middleware.process(context)

                log_event(
                    run_id=run_id,
                    node_name=middleware.name,
                    event_type="MIDDLEWARE",
                    summary="Executed successfully"
                )

                #  Lifecycle Authority Fix
                if context.get("terminal_status") == "ESCALATE":
                    update_status(run_id, "ESCALATED")
                    return context

                if context.get("terminal_status") == "WAITING_APPROVAL":
                    update_status(run_id, "WAITING_APPROVAL")
                    return context

            except MiddlewareException as e:
                context["terminal_status"] = "FAILED"

                update_status(run_id, "FAILED")

                log_event(
                    run_id=run_id,
                    node_name=middleware.name,
                    event_type="ERROR",
                    summary=str(e)
                )

                return context

        return context