from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.response import FileResponse
from pyramid.static import static_view
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, update, select
from sqlalchemy.sql import and_


import subprocess

import codecs
import os
import hashlib
import urlparse

# Global variables

# same as above, create meta-data
engine = create_engine('sqlite:///users.db', echo=True)
meta = MetaData()
meta.bind = engine
users_table = Table('users_table', meta, autoload=True)

workingDir = os.path.dirname(__file__)
projectDir = 'projects'
buildDir = 'build'

# Init
# Create project dir
if not os.path.exists(os.path.join(workingDir, projectDir)):
    os.makedirs(os.path.join(workingDir, projectDir))


@view_config(route_name='showDocument', renderer='pywebtex:templates/editor.pt')
def showDocument(request):
    projectHash = request.matchdict['projectHash']
    fileName = request.matchdict['fileName']

    projectPath = os.path.join(workingDir, projectDir, projectHash)
    path = os.path.join(workingDir, projectDir, projectHash, fileName)

    f = codecs.open(path, 'r', "utf-8")
    content = f.read()
    f.close()

    files = [f for f in os.listdir(
        projectPath) if os.path.isfile(os.path.join(projectPath, f))]

    directories = [f for f in os.listdir(
        projectPath) if os.path.isdir(os.path.join(projectPath, f))]

    return {'files': files, 'directories': directories, 'filename': fileName, 'editorcontent': content}


@view_config(route_name='home', renderer='pywebtex:templates/index.pt')
def home(request):

    relativePath = '.'
    styles = [relativePath + "/lib/bootstrap/css/bootstrap.min.css",
              relativePath + "/lib/jasny-bootstrap/css/jasny-bootstrap.min.css", relativePath + "/css/style.css"]
    scripts = [
        "http://ajax.googleapis.com/ajax/libs/jquery/2.0.0/jquery.min.js", "http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.3/jquery-ui.min.js",
        relativePath + "/lib/bootstrap/js/bootstrap.js", relativePath + "/lib/jasny-bootstrap/js/jasny-bootstrap.min.js", relativePath + '/js/app.js']
    return {'title': 'pyWebTeX', 'scripts': scripts, 'styles': styles}


@view_config(route_name='user', renderer='pywebtex:templates/user.pt')
def user(request):
    userName = request.matchdict['userName']

    return {'userName': userName, 'projects': 'Test'}


@view_config(route_name='register', renderer='json')
def register(request):
    userName = request.matchdict['userName']
    userPasswordHash = request.matchdict['userPasswordHash']

    return {'userName': userName, 'projects': 'Test'}


@view_config(route_name='openPDF', renderer='pywebtex:templates/pdfviewer.pt')
def openPDF(request):
    fileName = request.matchdict['fileName']
    projectHash = request.matchdict['projectHash']

    path = os.path.join(workingDir, projectDir, projectHash, 'build', fileName)
    pdfUrl = '../../../' + projectDir + '/' + \
        projectHash + '/' + buildDir + '/' + fileName
    return {'pdfPath': pdfUrl}


@view_config(route_name='new_project')
def newFile(request):
    fileName = request.POST.getone('fileName')
    projectName = request.POST.getone('projectName')
    projectHash = hashlib.sha1(projectName).hexdigest()

    print 'Creating project ' + projectName + ' in Folder ' + projectHash

    # Creating new file
    projectPath = os.path.join(workingDir, projectDir, projectHash)
    filePath = os.path.join(projectPath, fileName)

    if os.path.exists(projectPath):
        print 'Error creating project. Folder already used.'
        return Response('Error creating project. Folder already used.')
    else:
        os.makedirs(projectPath)

    f = codecs.open(filePath, 'w', "utf-8")
    f.close()

    print 'Init GIT'
    # Init the Git Repo
    gitInitArgs = ["git", "init"]
    gitInitProcess = subprocess.Popen(
        gitInitArgs, cwd=projectPath, shell=True)

    print 'Add File to GIT'

    # Add file
    gitAddArgs = ["git", "add", fileName]
    gitAddProcess = subprocess.Popen(
        gitAddArgs, cwd=projectPath)

    projectUrl = './' + projectHash + '/' + fileName
    return Response(projectUrl)


@view_config(route_name='saveFile')
def saveFile(request):

    projectHash = request.POST.getone('projectHash')
    fileName = request.POST.getone('fileName')
    content = request.POST.getone('content')

    path = os.path.join(workingDir, projectDir, projectHash, fileName)
    projectPath = os.path.join(workingDir, projectDir, projectHash)

    f = codecs.open(path, 'r+', "utf-8")
    f.write(content)
    f.close()

    # Add file
    gitArgs = ["git", "commit", "-m \"Auto Commit by pyWebTeX\""]
    gitProcess = subprocess.Popen(
        gitArgs, cwd=projectPath)

    return Response(fileName)


@view_config(route_name='uploadFile')
def uploadFile(request):

    fileName = request.POST['file'].filename
    input_file = request.POST['file'].file
    projectHash = request.POST['projectHash']
    outputPath = os.path.join(workingDir, projectDir, projectHash, fileName)

    output_file = open(outputPath, 'wb')
    input_file.seek(0)
    while True:
        data = input_file.read(2 << 16)
        if not data:
            break
        output_file.write(data)
    output_file.close()

    return Response(outputPath)


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

    compileArgs = ["latexmk", "-latexoption=\"-interaction=nonstopmode\"",
                   "-p", "-pdf", "-f", "-output-directory=./" + buildDir, fileName]
    compileProcess = subprocess.Popen(
        compileArgs, cwd=latexWorkingDir,  stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
    compileLog = compileProcess.communicate()[0]

    cleanArgs = ["latexmk", "-latexoption=\"-interaction=nonstopmode\"",
                 "-c", "-quiet", "-output-directory=./" + buildDir, fileName]
    subprocess.Popen(cleanArgs,  cwd=latexWorkingDir,
                     stdout=subprocess.PIPE,  stderr=subprocess.PIPE)

    pdfUrl = './' + buildDir + '/' + fileName[:-4] + '.pdf'
    return {'pdfUrl': pdfUrl, 'compileLog': compileLog}


if __name__ == '__main__':
    config = Configurator()
    config.add_route('showDocument', '/' +
                     projectDir + '/{projectHash}/{fileName}')
    config.add_route('new_project', '/api/project/new')
    config.add_route('saveFile', '/api/save')
    config.add_route('compile', '/api/compile')
    config.add_route('user', '/{userName}')
    config.add_route('register', '/api/user/register')
    config.add_route('home', '/')

    config.add_route(
        'openPDF',  '/pdf/{projectHash}/' + buildDir + '/{fileName}')
    config.add_route('uploadFile', '/api/file/upload')
    config.add_static_view(name='lib', path='pywebtex:lib')
    config.add_static_view(name='css', path='pywebtex:css')
    config.add_static_view(name='test', path='pywebtex:website')
    config.add_static_view(name='js', path='pywebtex:js')
    config.add_static_view(name='texlive', path='pywebtex:lib/texlive')
    config.add_route('showpdf', '/' + projectDir +
                     '/{projectHash}/' + buildDir + '/{fileName}')

    config.add_route('imageuploadform', '/upload')
    # upload processing
    # After replacing server/php/ in imageupload.pt with tal:attributes="action actionurl"
    # the following can be replaced with any URL base
    config.add_route('imageupload', '/server/php{sep:/*}{name:.*}')
    # retrieving images
    config.add_route('imageview', '/image/{name:.+}')
    config.add_static_view(name='', path='pywebtex:')
    config.scan()

    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
