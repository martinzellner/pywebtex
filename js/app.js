
$(document).ready(function() {
	// PDF

	PDFJS.disableWorker = true;

	var pdfDoc = null,
        pageNum = 1,
        scale = 0.8,
        canvas = document.getElementById('the-canvas'),
        ctx = canvas.getContext('2d');

    //
    // Get page info from document, resize canvas accordingly, and render page
    //
    function renderPage(num) {
      // Using promise to fetch the page
      pdfDoc.getPage(num).then(function(page) {
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
      document.getElementById('page_num').textContent = pageNum;
      document.getElementById('page_count').textContent = pdfDoc.numPages;
    }


 	var editor = ace.edit("editor");
    editor.setTheme("ace/theme/clouds");
    editor.getSession().setMode("ace/mode/latex");


    // APP

    // Paths
    var rootPath = window.location.origin;
    var apiPath = rootPath + '/api'

    // Messages
    var savedMessage = '<div class="alert alert-success">Saved.<a class="close" data-dismiss="alert" href="#">&times;</a></div>';
    var compileSuccessMessage = '<div class="alert  alert-success">Successfully compiled<a class="close" data-dismiss="alert" href="#">&times;</a></div>';
    var compilingMessage = '<div class="alert">Compiling...</div>';

    // State
    var currentProjectName = '';
    var currentProjectHash = window.location.pathname.split('/')[window.location.pathname.split('/').length-2];
    var currentFile = window.location.pathname.substring(window.location.pathname.lastIndexOf('/')+1);
    var currentLog = '';

    function compileDocument(){
    
        $('.marketing').before(compilingMessage).fadeIn(1000);

		$.post(apiPath + '/compile', { fileName: currentFile, projectHash : currentProjectHash,  content : editor.getValue()}, function(data){
			var path = data.pdfUrl;
			currentLog = data.compileLog;

			PDFJS.getDocument(path).then(function getPdfHelloWorld(_pdfDoc) {
    			pdfDoc = _pdfDoc;
     			renderPage(pageNum);
     			$('.alert').fadeOut();
				$('.marketing').before(compileSuccessMessage).fadeIn(500);
				$('.alert').fadeOut(5000);
    		});	
		});
    }

	$('#prev').click(function(){
	    if (pageNum <= 1)
	        return;
	    pageNum--;
	    renderPage(pageNum);
	 });

	$('#next').click(function(){
	    if (pageNum >= pdfDoc.numPages)
		      return;
	    pageNum++;
	    renderPage(pageNum);
	});

	// New Document
    $("#newDocumentDialog").modal({
		show: false
	});

     $(".document-log").popover({
     	placement: 'bottom',
     	html: true,
     	template: '<div class="popover popover-log"><div class="arrow"></div><div class="popover-inner  popover-log"><h3 class="popover-title popover-log"></h3><div class="popover-content popover-log"><p></p></div></div></div>',
     	content: function(){
     		var html = '<div id="logfile-container">' + currentLog.replace(/\n/g, '<br />') + "</div>";
     		return html;

     	}
	});


    $("#newDocumentDialog .save-button").click(function(){

	    currentProjectName = $('#newDocumentDialog .projectname').val();
	    currentFile = $('#newDocumentDialog .filename').val();

		$.post(apiPath + '/project/new', { projectName: currentProjectName, fileName: currentFile}, function(path){

			editor.setValue("");
			window.location.href = rootPath + '/projects/' + path;

		});

		$('#newDocumentDialog').modal('hide');
	});

    // Settings

     $("#settingsDialog").modal({
		show: false
 	});

    $("#settingsDialog .save-button").click(function(){
		$('#settingsDialog').modal('hide');
	});


	$('.document-save').click(function(){

		$.post(apiPath + '/save', { projectHash: currentProjectHash, fileName: currentFile, content : editor.getValue()}, function(filename){
           $('.marketing').before(savedMessage).fadeIn(500);
           $('.alert').fadeOut(2000);
  		});

	});

	$('.document-compile').click(function(){
		compileDocument();
	});


	compileDocument();
});

