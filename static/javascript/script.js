 // Design inspired 
 // Get the modal https://www.w3schools.com/howto/howto_css_modals.asp
 var modal = document.getElementById("myModal");

 // Get the <span> element that closes the modal
 var span = document.getElementsByClassName("close")[0];

 // When the user clicks on the button, open the modal
 function openModal(btn) {
   modal.style.display = "block";
   document.getElementById("current_student").innerHTML="@"+btn.getAttribute("data-username");

   document.getElementById("input_quiz1").value = document.getElementById(btn.getAttribute("data-username")+"_quiz1").innerHTML;
   document.getElementById("input_quiz2").value = document.getElementById(btn.getAttribute("data-username")+"_quiz2").innerHTML;
   document.getElementById("input_quiz3").value = document.getElementById(btn.getAttribute("data-username")+"_quiz3").innerHTML;
   document.getElementById("input_midtermexam").value = document.getElementById(btn.getAttribute("data-username")+"_midtermexam").innerHTML;
   document.getElementById("input_finalexam").value = document.getElementById(btn.getAttribute("data-username")+"_finalexam").innerHTML;
   document.getElementById("student_username").value = btn.getAttribute("data-username");
 }

 // When the user clicks on <span> (x), close the modal
 span.onclick = function() {
   modal.style.display = "none";
 }

 // When the user clicks anywhere outside of the modal, close it
 window.onclick = function(event) {
   if (event.target == modal) {
     modal.style.display = "none";
   }
 }