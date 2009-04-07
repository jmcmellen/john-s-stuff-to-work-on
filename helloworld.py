from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
class MainPage(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type']= 'text/html'
    self.response.out.write('''
<html><head><title>My app</title></head>
<body>
<h1>Hello, webapp World!</h1>
<p>What\'s going on?</p>
</body>
</html>''')
application = webapp.WSGIApplication(
                                     [('/', MainPage)],
                                     debug=True)

def main():
  run_wsgi_app(application)
if __name__ == "__main__":
  main()

