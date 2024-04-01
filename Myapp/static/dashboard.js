const menuBtn = document.querySelector('.menu-btn');
const editDetails = document.querySelector('.editDetails');
const recharge = document.querySelector('.recharge');
const editDetailsBlock = document.querySelector('.editDetailsBlock');
const rechargeBlock = document.querySelector('.rechargeBlock');
const homebtn = document.querySelector('.homebtn');
const balancesAndTable = document.querySelector('.balancesAndTable');
let menuOpen = false;

// menuBtn.addEventListener('click', () => {
//   if (!menuOpen) {
//     menuBtn.classList.add('open');
//     menuOpen = true;
//   } else {
//     menuBtn.classList.remove('open');
//     menuOpen = false;
//   }
// });
window.onload = displayNone();
let editDetailsClicked = false;
let homebtnClicked = false;
let rechargebtnClicked = false;

function displayNone() {
  editDetailsBlock.classList.add('open');
  rechargeBlock.classList.add('open');
}

editDetails.addEventListener('click', e => {
  // e.preventDefault()
  if (!editDetailsClicked) {
    balancesAndTable.classList.add('open');
    editDetailsBlock.classList.remove('open');
    rechargeBlock.classList.add('open');
  }
});

homebtn.addEventListener('click', e => {
  if (!homebtnClicked) {
    e.preventDefault();
    editDetailsBlock.classList.add('open');
    balancesAndTable.classList.remove('open');
    rechargeBlock.classList.add('open');
  }
});

recharge.addEventListener('click', e => {
  if (!rechargebtnClicked) {
    e.preventDefault();
    editDetailsBlock.classList.add('open');
    balancesAndTable.classList.add('open');
    rechargeBlock.classList.remove('open');
  }
});
