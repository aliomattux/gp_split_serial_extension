  	


openerp.customer_service = function (instance) {                                    

    instance.customer_service.action = function (parent, action) {        
		alert("Sign up is not allowed on this database.");	
	};

    instance.web.client_actions.add('customer_service_ticket.cs_notifier', 'instance.customer_service.action');

/*    
    instance.web.FormView = instance.web.FormView.extend({
      on_loaded: function() {
         	this._super.apply(this,arguments);
         	alert("Loaded");
         }
   });
*/
    
    // Web Events translated to pyhton execution - triggered js functions (with python call inside)
    function onLoadExecutionPython(){
    	
    	//do onload work
    	alert ("Onload event");
	}
	
	function SelectCustomerTicket(){
    	
    	//do onload work
    	alert ("Onload event");
	}
    
    
    
    
    
    
  /*  
    // Web Events translated to pyhton execution - listener registration
    if(window.addEventListener){
    	window.addEventListener('load',onLoadExecutionPython,false); //W3C
	} else{
    	window.attachEvent('onload',onLoadExecutionPython); //IE
	}
    
    
    */
};