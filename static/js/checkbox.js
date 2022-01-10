// CheckAll
$(function(){
 // Check or Uncheck All checkboxes
 $("#checkall").change(function(){
     var checked = $(this).is(':checked');
     if(checked){
         $(".checkbox").each(function(){
           $(this).prop("checked",true);
         });
     }else{
         $(".checkbox").each(function(){
           $(this).prop("checked",false);
         });
     }
     //updateStorage();
 });

 // Changing state of CheckAll checkbox
 $(".checkbox").click(function(){
     if($(".checkbox").length == $(".checkbox:checked").length) {
         $("#checkall").prop("checked", true);
      } else {
         $("#checkall").removeAttr("checked");
      }
  });
});
