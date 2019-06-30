/*!
 * Yacht Brain by BigLiveBait.com author: Rusty Coan
 * Copyright 2012-2020 YachtBrain
*/


function update_sensor_value(sensor_id){
	//alert('firing');
	//console.log('get_sensor_value firing');
	var alarm_low = parseInt($("#sensor_value_"+sensor_id).attr("alarm_low"));
	var warning_low = parseInt($("#sensor_value_"+sensor_id).attr("warning_low"));
	var warning_hi = parseInt($("#sensor_value_"+sensor_id).attr("warning_hi"));
	var alarm_hi = parseInt($("#sensor_value_"+sensor_id).attr("alarm_hi"));
	
	//console.log('preferred_currency == '+preferred_currency);
   	var response = jQuery.ajax({
	   type: "GET",
	   url:  "http://127.0.0.1:5000/getSensorValue?sensor_id="+sensor_id,
	   error: function(msg){
			event.preventDefault();
			// fail function here
			//alert("error");
			//alert("error"+msg);
			return false;
			var message = "<h3>An error has occured, your request has not been submitted.  Please contact us via Phone. We Apologize for any inconvenience.</h3>";
			jQuery("#"+responseID).append(message);
			jQuery("#"+responseID).css("display","block").fadeIn(1000);
			//return false;
			//alert('another err');
	
			},
	   success: function(msg){
			//event.preventDefault();
			// success function here
			//alert("success"+msg);
			//alert("response"+response);
			
			
			// setup a single array json object to concat
			
			
			var sensorValueJson = jQuery.parseJSON(msg);
			//console.log(sensorValueJson);
			//alert("success"+sensorValueJson['temp_f']);
//alert(typeof alarm_hi);

			// return the sensor values and the alarm status here
			jQuery("#sensor_value_"+sensor_id).text(sensorValueJson['temp_f']);
			jQuery("#sensor_value_"+sensor_id+"_metric_value").text(sensorValueJson['temp_c']);
			jQuery("#sensor_value_"+sensor_id+"_sae_value").text(sensorValueJson['temp_f']);
			
			if(!('webkitSpeechRecognition' in window)){
			alert('no speka da engrish');
			}
			var msg = new SpeechSynthesisUtterance('Hello World');
				window.speechSynthesis.speak(msg);
			
			// if we have an alarm status we change the color and blink the value
			// blink_me is the blinker class
			if(alarm_low && sensorValueJson['temp_f'] <= alarm_low){
				jQuery("#sensor_value_"+sensor_id).removeClass("yellow").addClass("red blink_me");				
			}
			else if(alarm_hi && sensorValueJson['temp_f'] >= alarm_hi){
				jQuery("#sensor_value_"+sensor_id).removeClass("yellow").addClass("red blink_me");				
			}
			else if(warning_low && sensorValueJson['temp_f'] <= warning_low){
				jQuery("#sensor_value_"+sensor_id).removeClass("red").addClass("yellow blink_me");				
			}
			else if(warning_hi && sensorValueJson['temp_f'] >= warning_hi){
				jQuery("#sensor_value_"+sensor_id).removeClass("red").addClass("yellow blink_me");				
			
				var msg = new SpeechSynthesisUtterance('Hello World');
				window.speechSynthesis.speak(msg);
			
			}
			else{
				jQuery("#sensor_value_"+sensor_id).removeClass("yellow red blink_me");
			}

			return false;
			//alert("success");
			//alertResponse(response);
			}
	
	 });
			
			
}// end sensor value


function refreshSensors(){
	//alert('here');
    // if a sensor value exists on the page we want to update them on a regular basis
    $(".sensor_value").each(function() {
        // "this" points to current item in looping through all elements with
        //alert($(this).attr("sensor_id"));
        update_sensor_value($(this).attr("sensor_id"));
    }); 

}


jQuery(document).ready(function(){
	if ($(".sensor_value").length > 0) {
		
		window.setInterval(function(){
		  /// call your function here
		  refreshSensors();
		}, 5000);
		
	}







$('.toggle_next').click(function () {     
    $(this).next().slideToggle();
    return false;
});





}); // end doc ready


////////////////////////////
/////
//// End yachtbrain
////
///////////////////////////





