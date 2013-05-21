
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

    function compileDocument(){
    	var url = window.location.pathname;
		var filename = url.substring(url.lastIndexOf('/')+1);
		var content = editor.getValue(); 
        $('.marketing').before('<div class="alert">Compiling...</div>').fadeIn(1000);
		$.post('../api/compile', { filename: filename, content : content}, function(responseCode){
			PDFJS.getDocument('../build/' + filename.slice(0, -4) + '.pdf').then(function getPdfHelloWorld(_pdfDoc) {
    			pdfDoc = _pdfDoc;
     			renderPage(pageNum);
    		});
			$('.alert').fadeOut();
			$('.marketing').before('<div class="alert  alert-success">Successfully compiled<a class="close" data-dismiss="alert" href="#">&times;</a></div>').fadeIn(500);
			$('.alert').fadeOut(5000);
			
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

    $("#newDocumentDialog .save-button").click(function(){
		$.post('../api/newfile', { filename: $('#newDocumentDialog .filename').val()}, function(filename){
			editor.setValue("");
			window.location.href = filename;
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
		var url = window.location.pathname;
		var filename = url.substring(url.lastIndexOf('/')+1);
		var content = editor.getValue(); 
		$.post('../api/save', { filename: filename, content : content}, function(filename){
           $('.marketing').before('<div class="alert alert-success">Saved.<a class="close" data-dismiss="alert" href="#">&times;</a></div>').fadeIn(500);
           $('.alert').fadeOut(2000);
  		});
	});

	$('.document-compile').click(function(){
		compileDocument();
	});


	compileDocument();
});

