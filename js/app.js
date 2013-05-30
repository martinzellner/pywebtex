var root = "../../";

$(document).ready(function() {

    // APP
    //
    // Get page info from document, resize canvas accordingly, and render page
    //
    var editor = ace.edit("editor");
    editor.setTheme("ace/theme/clouds");
    editor.getSession().setMode("ace/mode/latex");



    // PDF

    PDFJS.disableWorker = true;

    var pdfDoc = null,
        pageNum = 1,
        scale = 0.8,
        canvas = document.getElementById('the-canvas'),
        ctx = canvas.getContext('2d');

    function renderPage(num) {
        // Using promise to fetch the page
        pdfDoc.getPage(num)
            .then(function(page) {
            var viewport = page.getViewport(scale);
            canvas.height = 570;
            canvas.width = 500;

            // Render PDF page into canvas context
            var renderContext = {
                canvasContext: ctx,
                viewport: viewport
            };
            page.render(renderContext);
        });

        // Update page counters
        document.getElementById('page_num')
            .textContent = pageNum;
        document.getElementById('page_count')
            .textContent = pdfDoc.numPages;
    }

    // Paths
    var rootPath = window.location.origin;
    var apiPath = rootPath + '/api'

    // Messages
    var savedMessage = '<div class="alert alert-success">Saved.<a class="close" data-dismiss="alert" href="#">&times;</a></div>';
    var compileSuccessMessage = '<div class="alert  alert-success">Successfully compiled<a class="close" data-dismiss="alert" href="#">&times;</a></div>';
    var compilingMessage = '<div class="alert">Compiling...</div>';
    var compilingDownloadMessage = '<div class="alert">Downloading packages and compiling (with javascript)...</div>';

    // State
    var currentProjectName = '';
    var currentProjectHash = window.location.pathname.split('/')[window.location.pathname.split('/')
        .length - 2];
    var currentFile = window.location.pathname.substring(window.location.pathname.lastIndexOf('/') + 1);
    var currentLog = '';
    var BASE64_MARKER = ';base64,';


    function compileDocument() {
        $('.marketing').before(compilingMessage).fadeIn(1000);

        $.post(apiPath + '/compile', {
            fileName: currentFile,
            projectHash: currentProjectHash,
            content: editor.getValue()
        }, function(data) {
            var path = data.pdfUrl;
            currentLog = data.compileLog;

            PDFJS.getDocument(path).then(function getPdfHelloWorld(_pdfDoc) {
                pdfDoc = _pdfDoc;
                renderPage(pageNum);
                $('.alert')
                    .fadeOut();
                $('.marketing')
                    .before(compileSuccessMessage)
                    .fadeIn(500);
                $('.alert')
                    .fadeOut(5000);
            });
        });
    }

    $('#prev').click(function() {
        if (pageNum <= 1)
            return;
        pageNum--;
        renderPage(pageNum);
    });

    $('#next').click(function() {
        if (pageNum >= pdfDoc.numPages)
            return;
        pageNum++;
        renderPage(pageNum);
    });


    $('#openPdf').click(function() {
        window.open(rootPath + '/pdf/' + currentProjectHash + '/build/' + currentFile.split('.')[0] + '.pdf', '_blank');
    });

    $('#downloadPdf').click(function() {
        window.open(rootPath + '/projects/' + currentProjectHash + '/build/' + currentFile.split('.')[0] + '.pdf', '_blank');

    });

    $(".document-log").popover({
        placement: 'bottom',
        html: true,
        show: true,
        template: '<div class="popover popover-log"><div class="arrow"></div><div class="popover-inner  popover-log"><h3 class="popover-title popover-log"></h3><div class="popover-content popover-log"><p></p></div></div></div>',
        content: function() {
            var html = '<div id="logfile-container">' + currentLog.replace(/\n/g, '<br />') + "</div>";
            return html;

        }
    });

    $("#uploadFile").click(function() {
        $('#uploadDialog').modal(function() {
            $('.fileupload').fileupload();
        });
    });


    $('#login .btn-primary').click(function() {
        $('#login').modal('hide');
    });

    $('#register .btn-primary').click(function() {
        alert('Hello');
        $.post(apiPath + '/api/user/register', {
            userName: userName,
            userPasswordHash: userPasswordHash,
        });
        $('#register').modal('hide');
    });

    $(':file').change(function() {
        var file = this.files[0];
        name = file.name;
        size = file.size;
        type = file.type;
        //your validation
    });


    $('#upload-send').click(function() {
        var formData = new FormData();
        formData.append('file', $('#file-chooser')[0].files[0]);
        formData.append('projectHash', currentProjectHash);
        $.ajax({
            url: apiPath + '/file/upload', //server script to process data
            type: 'POST',
            // Form data
            data: formData,
            //Options to tell JQuery not to process data or worry about content-type
            contentType: false,
            processData: false,
        })
            .done(function() {
            $('.fileupload')
                .fileupload('reset');
            $('#uploadDialog')
                .modal('hide');
            window.location.href = currentFile;
        });
    });



    $("#newDocumentDialog .save-button").click(function() {

        currentProjectName = $('#newDocumentDialog .projectname').val();
        currentFile = $('#newDocumentDialog .filename').val();

        $.post(apiPath + '/project/new', {
            projectName: currentProjectName,
            fileName: currentFile
        }, function(path) {

            editor.setValue("");
            window.location.href = rootPath + '/projects/' + path;

        });

        $('#newDocumentDialog').modal('hide');
    });

    // Settings
    $("#settingsDialog .save-button").click(function() {
        $('#settingsDialog')
            .modal('hide');
    });


    $('.document-save').click(function() {

        $.post(apiPath + '/save', {
            projectHash: currentProjectHash,
            fileName: currentFile,
            content: editor.getValue()
        }, function(filename) {
            $('.marketing')
                .before(savedMessage)
                .fadeIn(500);
            $('.alert')
                .fadeOut(2000);
        });

    });

    function encode_utf8(s) {
        return unescape(encodeURIComponent(s));
    }

    function decode_utf8(s) {
        return decodeURIComponent(escape(s));
    }


    function convertDataURIToBinary(dataURI) {
        var base64Index = dataURI.indexOf(BASE64_MARKER) + BASE64_MARKER.length;
        var base64 = dataURI.substring(base64Index);
        var raw = window.atob(base64);
        var rawLength = raw.length;
        var array = new Uint8Array(new ArrayBuffer(rawLength));

        for (i = 0; i < rawLength; i++) {
            array[i] = raw.charCodeAt(i);
        }
        return array;
    }

    $('.document-compile').click(function() {
        compileDocument();

    });

    var button = $('.document-compile-client');
    button.click(function(ev) {
        $('.marketing')
            .before(compilingDownloadMessage)
            .fadeIn(1000);
        button.attr('disabled', 'disabled');
        button.addClass('disabled');

        var pdftex = new PDFTeX('../../lib/');
        window.pdftex = pdftex;

        pdftex.on_stdout = function(txt) {
            currentLog = currentLog + '<br>' + txt;
        }
        pdftex.on_stderr = function(txt) {
            currentLog = currentLog + '<br>' + txt;
        }

        var code = editor.getValue()

        downloadFiles(pdftex, document_files, function() {
            var texlive = new TeXLive(pdftex);

            texlive.compile(code, root, function(pdf) {
                button.removeAttr('disabled');
                button.removeClass('disabled');


                var pdfDataAsArray = convertDataURIToBinary('data:application/pdf;base64,' + window.btoa(pdf));

                // window.open('data:application/pdf;base64,' + window.btoa(pdf));

                PDFJS.getDocument(pdfDataAsArray)
                    .then(function getPdfHelloWorld(_pdfDoc) {
                    pdfDoc = _pdfDoc;
                    renderPage(pageNum);
                    $('.alert')
                        .fadeOut();
                    $('.marketing')
                        .before(compileSuccessMessage)
                        .fadeIn(500);
                    $('.alert')
                        .fadeOut(5000);
                });

                $('#navbar')
                    .append('<button id="open_pdf" class="btn">Open PDF</button>')
                    .find('#open_pdf')
                    .click(function() {});
            });
        });
    });

    var downloadFiles = function(pdftex, files, callback) {
        var pending = files.length;
        var cb = function() {
            pending--;
            if (pending === 0)
                callback();
        }

        for (var i in files) {
            pdftex.addUrl.apply(pdftex, files[i]).then(cb);
        }
    }

    var document_files = [
        [root + 'test.jpg', '/', 'test.jpg']
    ];

});