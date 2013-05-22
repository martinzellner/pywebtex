from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.response import FileResponse
import subprocess

import codecs
import os
import hashlib
import urlparse

# Global variables

workingDir = os.path.dirname(__file__)
projectDir = 'projects'
buildDir = 'build'

# Init
# Create project dir
if not os.path.exists(os.path.join(workingDir, projectDir)): os.makedirs(os.path.join(workingDir, projectDir))



@view_config(route_name='showDocument', renderer='pywebtex:templates/editor.pt')
def showDocument(request):
	projectHash =  request.matchdict['projectHash']
	fileName =  request.matchdict['fileName']

	path = os.path.join(workingDir, projectDir, projectHash, fileName)

	f = codecs.open(path, 'r', "utf-8")
	content = f.read()
	f.close()

	return  {'filename' : fileName, 'editorcontent' : content}

@view_config(route_name='new_project')
def newFile(request):
	fileName = request.POST.getone('fileName')
	projectName = request.POST.getone('projectName')
	projectHash = hashlib.sha1(projectName).hexdigest()

	print 'Creating project ' + projectName + ' in Folder ' + projectHash

	# Creating new file
	projectPath = os.path.join(workingDir, projectDir, projectHash)
	if os.path.exists(projectPath):
		print 'Error creating project. Folder already used.'
		return Response('Error creating project. Folder already used.')
	else:
		os.makedirs(projectPath)

	filePath = os.path.join(projectPath, fileName)
	f = codecs.open(filePath, 'w', "utf-8")
	f.close()


	projectUrl = './' + projectHash + '/' + fileName
	return Response(projectUrl)

@view_config(route_name='saveFile')
def saveFile(request):

	projectHash = request.POST.getone('projectHash')
	fileName = request.POST.getone('fileName')
	content = request.POST.getone('content')

	path = os.path.join(workingDir, projectDir, projectHash, fileName)

	f = codecs.open(path, 'r+', "utf-8")
	f.write(content)
	f.close()

	return Response(fileName)

@view_config(route_name='showpdf')
def showpdf(request):
	fileName = request.matchdict['fileName']
	projectHash = request.matchdict['projectHash']

	path = os.path.join(workingDir, projectDir, projectHash, 'build', fileName)
	return FileResponse(path)

@view_config(route_name='compile', renderer='json')
def compile(request):
	projectHash = request.POST.getone('projectHash')
	fileName = request.POST.getone('fileName')
	content = request.POST.getone('content')

	latexWorkingDir = os.path.join(workingDir, projectDir, projectHash)
	latexBuildDir = os.path.join(latexWorkingDir, buildDir)
	latexFilePath = os.path.join(latexWorkingDir, fileName)

	f = codecs.open(latexFilePath, 'r+', "utf-8")
	f.write(content)
	f.close()

	compileArgs =["latexmk", "-latexoption=\"-interaction=nonstopmode\"", "-p", "-pdf", "-f", "-output-directory=./" + buildDir, fileName]
	compileProcess = subprocess.Popen(compileArgs, cwd=latexWorkingDir,  stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
	compileLog = compileProcess.communicate()[0]

	cleanArgs = ["latexmk", "-latexoption=\"-interaction=nonstopmode\"", "-c", "-quiet", "-output-directory=./" + buildDir, fileName]
	subprocess.Popen(cleanArgs,  cwd=latexWorkingDir, stdout=subprocess.PIPE,  stderr=subprocess.PIPE)

	
	pdfUrl = './' + buildDir + '/' + fileName[:-4] + '.pdf'
	return {'pdfUrl' : pdfUrl, 'compileLog': compileLog}


if __name__ == '__main__':
    config = Configurator()
    config.add_route('showDocument', '/' + projectDir + '/{projectHash}/{fileName}')
    config.add_route('new_project', '/api/project/new')
    config.add_route('saveFile', '/api/save')
    config.add_route('compile', '/api/compile')
    config.add_static_view(name='lib', path='pywebtex:lib')
    config.add_static_view(name='css', path='pywebtex:css')
    config.add_static_view(name='js', path='pywebtex:js')
    config.add_route('showpdf', '/' + projectDir + '/{projectHash}/' + buildDir + '/{fileName}')
    config.scan()

    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
