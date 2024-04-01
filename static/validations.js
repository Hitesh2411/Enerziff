function validateEmail() {
    console.log("validateemail is calling")
    var emailInput = document.getElementsById('user_email');
    var emailMessage = document.getElementById('emailMessage');
    
    // Check if the entered email ends with "gmail.com"
    if (emailInput.value.toLowerCase().endsWith('gmail.com')) {
      emailMessage.textContent = ''; // Clear the error message
    } else {
      emailMessage.textContent = 'Please enter a valid Gmail address.';
    }
  }
  function validateEmail2() {
    console.log("validateemail is calling")
    var emailInput2 = document.getElementsById('user_email2');
    var emailMessage2 = document.getElementById('emailMessage2');
    
    // Check if the entered email ends with "gmail.com"
    if (emailInput2.value.toLowerCase().endsWith('gmail.com')) {
      emailMessage2.textContent = ''; // Clear the error message
    } else {
      emailMessage2.textContent = 'Please enter a valid Gmail address.';
    }
  }