searchVisible = 0;
transparent = true;

$(document).ready(function(){
    /*  Activate the tooltips      */
    $('[rel="tooltip"]').tooltip();
      
    $('.wizard-card').bootstrapWizard({
        'tabClass': 'nav nav-pills',
        'nextSelector': '.btn-next',
        'previousSelector': '.btn-previous',
         
         onInit : function(tab, navigation, index){
            
           //check number of tabs and fill the entire row
           var $total = navigation.find('li').length;
           $width = 100/$total;
           
           $display_width = $(document).width();
           
           if($display_width < 600 && $total > 3){
               $width = 50;
           }
           
           navigation.find('li').css('width',$width + '%');
           
        },
        onNext: function(tab, navigation, index){
            if(index == 1){
              return validateFirstStep();
            } else if(index == 2){
                return validateSecondStep();
            } else if(index == 3){
                return validateThirdStep();
            } //etc. 
              
        },
        onTabClick : function(tab, navigation, index){
            // Disable the possibility to click on tabs
            return false;
        }, 
        onTabShow: function(tab, navigation, index) {
            var $total = navigation.find('li').length;
            var $current = index+1;            
            var wizard = navigation.closest('.wizard-card');
            console.log(wizard)
            // If it's the last tab then hide the last button and show the finish instead
            if($current >= $total) {
                $(wizard).find('.btn-next').hide();
                $(wizard).find('.btn-finish').show();
            } else {
                $(wizard).find('.btn-next').show();
                $(wizard).find('.btn-finish').hide();
            }
        }
    });

    // Prepare the preview for profile picture
    $("#wizard-picture").change(function(){
        readURL(this);
    });
    
    $('[data-toggle="wizard-radio"]').click(function(){
        wizard = $(this).closest('.wizard-card');
        wizard.find('[data-toggle="wizard-radio"]').removeClass('active');
        $(this).addClass('active');
        $(wizard).find('[type="radio"]').removeAttr('checked');
        $(this).find('[type="radio"]').attr('checked','true');
    });
    
    $('[data-toggle="wizard-checkbox"]').click(function(){
        if( $(this).hasClass('active')){
            $(this).removeClass('active');
            $(this).find('[type="checkbox"]').removeAttr('checked');
        } else {
            $(this).addClass('active');
            $(this).find('[type="checkbox"]').attr('checked','true');
        }
    });
    
    $height = $(document).height();
    $('.set-full-height').css('height',$height);
    
    
});

function validateFirstStep(){
    
    $(".wizard-card form").validate({
		rules: {
			title: "required",
			description: "required",
			amt_keywords: "required",
			organization_name: "required",
			contact_email_on_error: {
				required: true,
				email: true
			},
                        dbhost: "required",
                        dbname: "required",
                        dbusername: "required",
                        dbtable: "required",
			dbpassword: {
				required: true,
				minlength: 5
			},
			dbpasswordconfirm: {
				required: true,
				minlength: 5,
				equalTo: "#dbpassword"
			}

                
		},
		messages: {
			title: "Please choose a title for your experiment.",
			description: "Please describe your experiment.",
			amt_keywords: "Please list kewords, separated by commas",
			organization_name: "Please provide an organization.",
			contact_email_on_error: "Please provide a contact email.",
		}
	}); 
	
	if(!$(".wizard-card form").valid()){
    	    return false;
	}
	return true;
}

function validateSecondStep(){
   
    //code here for second step
    $(".wizard-card form").validate({
		rules: {
		
                        dbhost: "required",
                        dbname: "required",
                        dbusername: "required",
                        dbtable: "required",
			dbpassword: {
				required: true,
				minlength: 5
			},
			dbpasswordconfirm: {
				required: true,
				minlength: 5,
				equalTo: "#dbpassword"
			},
		
		},
		messages: {
			
                        dbhost: "Please provide a database host",
                        dbname: "Please specify a database name",
                        dbusername: "Please specify a username",
                        dbtable: "Please specify a table."
		}
	}); 
	
	if(!$(".wizard-card form").valid()){
    	console.log('invalid');
    	return false;
	}
	return true;
    
}

function validateThirdStep(){
 
    //code here for second step
    $(".wizard-card form").validate({
		rules: {
		
                        deploychoice: "required",
		
		},
		messages: {
			
                        deploychoice: "Please select your deployment",
		}
	}); 
	
	if(!$(".wizard-card form").valid()){
    	console.log('invalid');
    	return false;
	}
	return true;
    
    
}

//Function to show image before upload

function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            $('#wizardPicturePreview').attr('src', e.target.result).fadeIn('slow');
        }
        reader.readAsDataURL(input.files[0]);
    }
}
