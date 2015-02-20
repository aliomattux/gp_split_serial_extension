


function CreateTextAreaWithDupAlert(id) {

	// Make tone
	function duplicate_alert() {
		
		/*
		var audio = new Audio('http://www.rangde.org/static/bell-ring-01.mp3');
		audio.play();		
	   	alert ("dup");
		*/
       var audioElement = document.createElement('audio');
        audioElement.setAttribute('src', 'http://www.rangde.org/static/bell-ring-01.mp3');
        audioElement.setAttribute('autoplay', 'autoplay');
        //audioElement.load()

        $.get();

        audioElement.addEventListener("load", function() {
            audioElement.play();
        }, true);
		//audioElement.play();
		
	}
	
	
	// Check for duplicates
	// Break list apart and check the last item against the top items
	function duplicate_check(list) {
		
		scanned_list = list.split("\n");
		token = scanned_list[scanned_list.length-2];
		
		if (token != '\n') { 
			for (i=0;i<=scanned_list.length-3;i++) {
				if (scanned_list[i] == token)
					return true;
			}
		}
		
		// no dupes	
		return false;
	} 

	var textarea = $(document.getElementsByName(id)[0]); //$(id)[0]; //document.getElementsByName(id)[0]; //$(id)[0];	

		/* React to the scroll event */
		textarea.keyup( function(tn){
			
			var domTextArea		= $(this)[0];
			
			// Check if item is inputted in a newline
			test_area_content = domTextArea.value;
			text_area_length = test_area_content.length;
			last_character = test_area_content[test_area_content.length-1];
			if (test_area_content[test_area_content.length-1]== '\n') {	
			
				// Alert duplicates
				if (duplicate_check(test_area_content)) {					
					duplicate_alert();
				}
			}
			
		});	
	
	
} // function CreateTextAreaWithDupAlert(id) {






// Produces line numbers and alerts, however doesn't do well with lines counts over 2000
function CreateTextAreaWithLinesAndAlert(id) {

	// Helpers
	// Make tone
	function duplicate_alert() {
		
		/*
		var audio = new Audio('http://www.rangde.org/static/bell-ring-01.mp3');
		audio.play();		
	   	alert ("dup");
		*/
       var audioElement = document.createElement('audio');
        audioElement.setAttribute('src', 'http://www.rangde.org/static/bell-ring-01.mp3');
        audioElement.setAttribute('autoplay', 'autoplay');
        //audioElement.load()

        $.get();

        audioElement.addEventListener("load", function() {
            audioElement.play();
        }, true);
		//audioElement.play();
		
	}
	
	
	// Check for duplicates
	// Break list apart and check the last item against the top items
	function duplicate_check(list) {
		
		scanned_list = list.split("\n");
		token = scanned_list[scanned_list.length-2];
		
		if (token != '\n') { 
			for (i=0;i<=scanned_list.length-3;i++) {
				if (scanned_list[i] == token)
					return true;
			}
		}
		
		// no dupes	
		return false;
	} 
	
	
	
	/*
	 * Helper function to make sure the line numbers are always
	 * kept up to the current system
	 */
	var fillOutLines = function(codeLines, h, lineNo){
		while ( (codeLines.height() - h - 2) <= 0 ){
			/*if ( lineNo == opts.selectedLine )
				codeLines.append("<div class='lineno lineselect'>" + lineNo + "</div>");
			else*/
			codeLines.append("<div class='lineno' >" + lineNo + "</div>");			
			lineNo++;
		}
		return lineNo;
	};
	//style='text-align:right'
	//style='text-align:right'
	/*
	 * Iterate through each of the elements are to be applied to
	 */
	//return this.each(function() {
		var lineNo = 1;
		var textarea = $(document.getElementsByName(id)[0]); //$(id)[0]; //document.getElementsByName(id)[0]; //$(id)[0];
		


		
		/* Turn off the wrapping of as we don't want to screw up the line numbers */
		textarea.attr("wrap", "off");
		textarea.css({resize:'none'});
		var originalTextAreaWidth	= textarea.outerWidth();

		/* Wrap the text area in the elements we need */
		textarea.wrap("<div class='linedtextarea'></div>");
		var linedTextAreaDiv	= textarea.parent().wrap("<div class='linedwrap' style='width:" + originalTextAreaWidth + "px'></div>");
		var linedWrapDiv 			= linedTextAreaDiv.parent();
		linedWrapDiv.prepend("<div class='lines' style='width:50px'></div>");

		var linesDiv	= linedWrapDiv.find(".lines");
		linesDiv.height( textarea.height() + 6 );
		linesDiv_pos = linesDiv.position();
		
	
		
		// format for browser type
		var nAgt = navigator.userAgent;
		if ((verOffset=nAgt.indexOf("Firefox"))!=-1) {
		/*	linesDiv.css({
			
        		//position: "relative",
        		top: -110 + "px",

    	  	}).show(); 
			*/
			textarea.css({
        		position: "absolute",
        		top: 153 + "px",
        		left: 230 + "px"
    	  	}).show();
			
			/*
			textarea.css({
        		position: "relative",
        		top: -122 + "px",
        		left: 40 + "px"
    	  	}).show();
    	  	*/
		 } else if ((verOffset=nAgt.indexOf("Chrome"))!=-1) {
			 
			linesDiv.css({
        		//position: "relative",
        		//top: -120 + "px",

    	  	}).show(); 
			 
			textarea.css({
        		position: "absolute",
        		top: linesDiv_pos.top - 4 + "px",
        		left: linesDiv_pos.left + 38 + "px"
    	  	}).show();
			
		 } else {
			 textarea.css({
        		position: "relative",
        		top: -95 + "px",
        		left: 40 + "px"
			 }).show();
		 }
		
										
		/* Draw the number bar; filling it out where necessary */
		linesDiv.append( "<div class='codelines' style='font-family: \"Helvetica Neue\",Helvetica,Arial,sans-serif;font-size: 1em;' ></div>" );
		var codeLinesDiv	= linesDiv.find(".codelines");
		lineNo = fillOutLines( codeLinesDiv, linesDiv.height(), 1 );

		/* Move the textarea to the selected line */ 
		/*if ( opts.selectedLine != -1 && !isNaN(opts.selectedLine) ){
			var fontSize = parseInt( textarea.height() / (lineNo-2) );
			var position = parseInt( fontSize * opts.selectedLine ) - (textarea.height()/2);
			textarea[0].scrollTop = position;
		}*/

		
		/* Set the width */
		var sidebarWidth					= linesDiv.outerWidth();
		var paddingHorizontal 		= parseInt( linedWrapDiv.css("border-left-width") ) + parseInt( linedWrapDiv.css("border-right-width") ) + parseInt( linedWrapDiv.css("padding-left") ) + parseInt( linedWrapDiv.css("padding-right") );
		var linedWrapDivNewWidth 	= originalTextAreaWidth - paddingHorizontal;
		var textareaNewWidth			= originalTextAreaWidth - sidebarWidth - paddingHorizontal - 20;

		textarea.width( textareaNewWidth );
		//linedWrapDiv.width( linedWrapDivNewWidth );
		

		
		/* React to the scroll event */
		textarea.scroll( function(tn){
			var domTextArea		= $(this)[0];
			var scrollTop 		= domTextArea.scrollTop;
			var clientHeight 	= domTextArea.clientHeight;
			codeLinesDiv.css( {'margin-top': (-1*scrollTop) + "px"} );
			lineNo = fillOutLines( codeLinesDiv, scrollTop + clientHeight, lineNo );
		});
		
				/* React to the scroll event */
		textarea.keyup( function(tn){
			
			var domTextArea		= $(this)[0];
			
			// Check if item is inputted in a newline
			test_area_content = domTextArea.value;
			text_area_length = test_area_content.length;
			last_character = test_area_content[test_area_content.length-1];
			if (test_area_content[test_area_content.length-1]== '\n') {	
			
				// Alert duplicates
				if (duplicate_check(test_area_content)) {					
					duplicate_alert();
				}
				
				// Trim the textarea
				//domTextArea.value = test_area_content.trim();
				
				// Continue line numbers
				var scrollTop 		= domTextArea.scrollTop;
				var clientHeight 	= domTextArea.clientHeight;
				codeLinesDiv.css( {'margin-top': (-1*scrollTop) + "px"} );
				lineNo = fillOutLines( codeLinesDiv, scrollTop + clientHeight, lineNo );
			}
			
		});

		//ta.onkeyup      = function() { setLine(); }

		/* Should the textarea get resized outside of our control */
		textarea.resize( function(tn){
			var domTextArea	= $(this)[0];
			linesDiv.height( domTextArea.clientHeight + 6 );
		});

	//});
	
	/*
};

// default options
$.fn.linedtextarea.defaults = {
	selectedLine: -1,
	selectedClass: 'lineselect'
};
	
*/	
	
} //function CreateTextAreaWithLinesAndAlert(id) 


/*
function createTextAreaWithLines(id) {
          var el = document.createElement('TEXTAREA');
          var ta = document.getElementsByName(id)[0];
          var string = '';
            for(var no=1;no<300;no++){
              if(string.length>0)string += "&#10;";
              string += no;              
            }
          el.className      = 'textAreaWithLines';
          el.style.height   = (ta.offsetHeight-4) + "px";
          el.style.left
          el.style.width    = "25px";
          el.style.position = "absolute";
          el.style.overflow = 'hidden';
          el.style.textAlign = 'right';
          el.style.paddingRight = '0.2em';
          el.innerHTML      = string;  //Firefox renders \n linebreak
          el.innerText      = string; //IE6 renders \n line break
          el.style.zIndex   =   0;
          //ta.style.zIndex   = 1;
          
          ta.style.position = "relative";
          ta.style.left = '60px';
          ta.style.width    = "450px";
          ta.parentNode.insertBefore(el, ta.nextSibling);
          setLine();
          ta.focus();
     
          ta.onkeyup      = function() { setLine(); }
          ta.onkeydown    = function() { setLine(); }
          ta.onmousedown  = function() { setLine(); }
          ta.onscroll     = function() { setLine(); }
          ta.onblur       = function() { setLine(); }
          ta.onfocus      = function() { setLine(); }
          ta.onmouseover  = function() { setLine(); }
          ta.onmouseup    = function() { setLine(); }
               
         function setLine(){
           el.scrollTop   = ta.scrollTop;
           el.style.top   = (ta.offsetTop) + "px";
            el.style.left  = (ta.offsetLeft - 62) + "px";
            el.style.height   = (ta.offsetHeight) + "px";
         }
} */