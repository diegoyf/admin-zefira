import tornado.web

class UserModule(tornado.web.UIModule):
	def render(self, user):
		return self.render_string(
			"modules/user.html",
			user = user,
			)

class UserCoModule(tornado.web.UIModule):
	def render(self, user):
		return self.render_string(
			"modules/userco.html",
			user = user,
			)		