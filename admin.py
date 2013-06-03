import tornado.web
import tornado.ioloop
import tornado.httpserver
import os.path
import uimodules
import logging

from tornado.options import define, options
from datamanag import DataManagement

define("port", default = 8000, help= "run on given port", type=int)


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
        (r"/" , AdminMainHandler),
        (r"/admin-home", AdminHomeHandler),
        (r"/logout", LogoutHandler),
        (r"/error", ErrorHandler),
        (r"/admin-people", AdminPeopleHandler),
        (r"/admin-companies", AdminCompaniesHandler),
        (r"/edit", EditHandler),
        (r"/delete", DeleteHandler),
        (r"/create-user", CreateUserHandler )
        ]

        settings = dict(
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path = os.path.join(os.path.dirname(__file__),"static"),
            ui_modules={
                
                "User": uimodules.UserModule,
                "UserCo": uimodules.UserCoModule
               
             } ,         
            debug = True,
            cookie_secret = "0azgrztWSuenSRWevq9GAOp/4bDtSET0q8YII0ZfLDc=",
            login_url = "/",
            xsrf_cookies = True,
            autoescape = None,
            
            )

        self.dataManager = DataManagement("zefira")


        tornado.web.Application.__init__(self, handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    
    #Decorador que retorna una instancia de la clase administrador
    #para ser utilizada por la aplicacion
    @property
    def data_manager(self):
        return self.application.dataManager

    #Funcion que utiliza los parametros seguros de LoginHandler para
    #llamar el usuario y retornar una array con su informacion
    def get_current_user(self):
        email  = self.get_secure_cookie("email")
        password = self.get_secure_cookie("password")
        
        
        user = self.application.dataManager.fetch_admin(email, password)
        if user:
            return user
        else:
            self.redirect("/error")

class AdminMainHandler(tornado.web.RequestHandler):
    
    def get(self):
        self.render(
            "admin-main.html",
            page_title ="Zefira Admin | Login",
            header_text = "Zefira"
            )

    def post(self):

        self.set_secure_cookie("email", self.get_argument("email"))
        self.set_secure_cookie("password", self.get_argument("password"))
        self.redirect("/admin-home")

class AdminHomeHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self):

        companies_count = self.data_manager.get_user_count("companies")
        people_count = self.data_manager.get_user_count("people") 
        self.render(
            "admin-home.html",
            page_title ="Zefira Admin | Home",
            people_count = people_count,
            companies_count = companies_count

            )

class LogoutHandler(tornado.web.RequestHandler):
    
    def get(self):
        self.clear_cookie("email")
        self.clear_cookie("password")
        self.redirect("/")

class AdminPeopleHandler(BaseHandler):
    def get(self):

        users = self.data_manager.fetch_users_admin("people")

        self.render(
            "admin-people.html",
            page_title = "Zefira Admin | People",
            users = users,

            ) 

class AdminCompaniesHandler(BaseHandler):
    
    def get(self):

        users = self.data_manager.fetch_users_admin("companies")
        self.render(
            "admin-companies.html",
            page_title = "Zefira Admin | Companies",
            users = users,
            ) 

class EditHandler(BaseHandler):
    def get(self):
        user_id = self.get_argument("user_id", None)
        branch = self.get_argument("branch", None)

        user_info = self.data_manager.fetch_user_info(user_id, branch)
        
        self.render(
            "edit-user.html",
            page_title="Zefira Admin | Edit User",
            user_info = user_info,
            branch = branch
            )
    def post(self):
        branch = self.get_argument("branch", None)
        logging.info(self.request.arguments)
        logging.info(branch)
        success = self.data_manager.save_user(self.request.arguments, branch)
        logging.info(success)
        if success=="ok":
            if branch == "people":
                self.redirect("/admin-people")
            else:
                self.redirect("/admin-companies")    
        else:
            self.redirect("/error")

class DeleteHandler(BaseHandler):
    def get(self):
        user_id = self.get_argument("user_id", None)
        branch = self.get_argument("branch", None)

        success = self.data_manager.delete_user(user_id, branch)

        if success:
            if branch == "people":
                self.redirect("/admin-people")
            else:
                self.redirect("/admin-companies")    
        else:
            self.redirect("/error")      
class CreateUserHandler(BaseHandler):

     def post(self):
        branch = self.get_argument("branch", None)
        success = self.data_manager.create_user(self.request.arguments, branch)

        if success:
            if branch == "people":
                self.redirect("/admin-people")
            else:
                self.redirect("/admin-companies")
        else:
            self.redirect("/error")                

class ErrorHandler(tornado.web.RequestHandler):
    
    def get(self):
        self.write("Error ")        

def main():

    tornado.options.parse_command_line()
    server = tornado.httpserver.HTTPServer(Application())
    server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()