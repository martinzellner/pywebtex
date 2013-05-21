from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.view import view_config
from pyramid.response import Response
import codecs
import subprocess 
import email.utils

@view_config(route_name='showDocument', renderer='pytex:templates/editor.pt')
def showDocument(request):
	docName =  request.matchdict['docName']
	f = codecs.open('files/' + docName, 'r', "utf-8")
	content = f.read()
	f.close()
	return  {'editorcontent' : content}

@view_config(route_name='newFile')
def newFile(request):
	fileName = request.POST.getone('filename')
	f = codecs.open('files/' + fileName, 'w', "utf-8")
	f.close()
	return Response(fileName)

@view_config(route_name='saveFile')
def saveFile(request):
	fileName = request.POST.getone('filename')
	content = request.POST.getone('content')
	f = codecs.open('files/' + fileName, 'r+', "utf-8")
	f.write(content)
	f.close()
	return Response(fileName)

@view_config(route_name='compile')
def compile(request):
	fileName = request.POST.getone('filename')
	content = request.POST.getone('content')
	f = codecs.open('files/' + fileName, 'r+', "utf-8")
	f.write(content)
	f.close()
	errorCode = subprocess.call(" latexmk  -p  -pdf -f -quiet -output-directory=./build/  files/" + fileName,  shell=True)
	
	subprocess.call("latexmk -c -output-directory=./build/  files/" + fileName,  shell=True)
	return Response(str(errorCode))


if __name__ == '__main__':
    config = Configurator()
    config.add_route('showDocument', '/file/{docName}')
    config.add_route('newFile', '/api/newfile')
    config.add_route('saveFile', '/api/save')
    config.add_route('compile', '/api/compile')
    config.add_static_view(name='lib', path='pytex:lib')
    config.add_static_view(name='build', path='pytex:build')
    config.scan()

    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
