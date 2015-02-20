/*
$(document).ready(function(){
	alert("Hello");    	  
    $(function() {
    	alert("I'm Inside"); 
  		// Target all classed with ".lined"
  		$(".lined").linedtextarea(
    		{selectedLine: 1}
  		);

  		// Target a single one
  		//$("#barcode_text_area").linedtextarea();
	});
});
*/

openerp.web_example = function (instance) {
    console.log("GABE!!! Module loaded");
    alert ("Hello, world!");
};

/*
 openerp.web_example = function (instance) {
     instance.web.client_actions.add('example.action', 'instance.web_example.Action');
     instance.web_example.Action = instance.web.Widget.extend({
        template: 'web_example.action'
        className: 'oe_web_example',
        start: function () {
            this.$el.text("Hello, world!");
            return this._super();
        }
     });
 };
*/