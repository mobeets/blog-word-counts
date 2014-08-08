import cherrypy
from mako.lookup import TemplateLookup

import conf
import bin.gviz_api
import bin.model

lookup = TemplateLookup(directories=['templates'])
class Root(object):
    def __init__(self):
        pass

    @cherrypy.expose
    def default(self, *inurl, **data):
        blog_name = None
        errors = None
        if inurl:
            blog_name = '/'.join(inurl)
        if data or cherrypy.request.method == 'POST':
            raise cherrypy.HTTPRedirect('/' + data['blog_name'])
        json = self.process_data(blog_name, errors)
        errors = '<br>'.join(errors) if errors else ''
        json = json if not errors else None
        tmp = lookup.get_template('index.html')
        return tmp.render(json=json, errors=errors)

    def make_gviz_json(self, wcs):
        description = [("Date", "date"), ("Word Count", "number"), ("Title", "string"), ("Description", "string")]
        data_table = bin.gviz_api.DataTable(description)
        data_table.LoadData([[date, wc, title, ''] for date, wc, title in wcs])
        return data_table.ToJSon()

    def process_data(self, blog_name, errors):
        if not blog_name:
            return
        try:
            wcs = bin.model.get_sorted_word_counts_of_posts_in(blog_name)
        except:
            wcs = []
            errors.append("Sorry, this isn't working for some reason.")
            errors.append("(This might only work for blogs hosted on tumblr and blogspot.)")
        return self.make_gviz_json(wcs)

def main():
    cherrypy.config.update(conf.settings)
    root_app = cherrypy.tree.mount(Root(), '/', conf.root_settings)
    root_app.merge(conf.settings)

    if hasattr(cherrypy.engine, "signal_handler"):
        cherrypy.engine.signal_handler.subscribe()
    if hasattr(cherrypy.engine, "console_control_handler"):
        cherrypy.engine.console_control_handler.subscribe()
    cherrypy.engine.start()
    cherrypy.engine.block()

if __name__ == '__main__':
    main()
