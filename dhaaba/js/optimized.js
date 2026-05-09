// Optimized JavaScript for better performance
// Minified version of script.js with only essential functionality

// DOM Elements
const menuToggle=document.querySelector('.menu-toggle');
const navMenu=document.querySelector('.nav-menu');
const searchBtn=document.querySelector('.search-btn');
const searchOverlay=document.querySelector('.search-overlay');
const closeSearch=document.querySelector('.close-search');
const cartBtn=document.querySelector('.cart-btn');
const cartSidebar=document.querySelector('.cart-sidebar');
const closeCart=document.querySelector('.close-cart');
const filterBtns=document.querySelectorAll('.filter-btn');
const productCards=document.querySelectorAll('.product-card');
const addToCartBtns=document.querySelectorAll('.add-to-cart');

// Mobile Menu Toggle
menuToggle&&menuToggle.addEventListener('click',()=>{navMenu.style.display=navMenu.style.display==='flex'?'none':'flex';});

// Search Overlay
searchBtn&&searchBtn.addEventListener('click',()=>{searchOverlay.classList.add('active');});
closeSearch&&closeSearch.addEventListener('click',()=>{searchOverlay.classList.remove('active');});
searchOverlay&&searchOverlay.addEventListener('click',(e)=>{e.target===searchOverlay&&searchOverlay.classList.remove('active');});

// Cart Sidebar
cartBtn&&cartBtn.addEventListener('click',()=>{cartSidebar.classList.add('active');});
closeCart&&closeCart.addEventListener('click',()=>{cartSidebar.classList.remove('active');});
cartSidebar&&cartSidebar.addEventListener('click',(e)=>{e.target===cartSidebar&&cartSidebar.classList.remove('active');});

// Product Filtering
filterBtns.forEach(btn=>{btn.addEventListener('click',()=>{filterBtns.forEach(b=>b.classList.remove('active'));btn.classList.add('active');const filter=btn.getAttribute('data-filter');productCards.forEach(card=>{if(filter==='all'||card.getAttribute('data-category')===filter){card.style.display='block';}else{card.style.display='none';}});});});

// Shopping Cart Functionality
let cartItems=[];let itemCount=0;
function updateCartCount(){const count=document.querySelector('.cart-count');count&&(count.textContent=itemCount);}
function addToCart(name,price){const existing=cartItems.find(item=>item.name===name);if(existing){existing.quantity+=1;}else{cartItems.push({name,price,quantity:1});}itemCount++;updateCartCount();showNotification(`${name} added to cart!`);}
addToCartBtns.forEach(btn=>{btn.addEventListener('click',(e)=>{const card=e.target.closest('.product-card');const name=card.querySelector('h3').textContent;const priceText=card.querySelector('.price').textContent;const price=parseInt(priceText.replace('₹',''));addToCart(name,price);});});

// Notification System
function showNotification(message){const existing=document.querySelector('.notification');existing&&existing.remove();const n=document.createElement('div');n.className='notification';n.textContent=message;Object.assign(n.style,{position:'fixed',top:'20px',right:'20px',backgroundColor:'#4ECDC4',color:'white',padding:'15px 20px',borderRadius:'8px',boxShadow:'0 4px 12px rgba(0,0,0,0.15)',zIndex:'1300',transform:'translateX(100%)',transition:'transform 0.3s ease'});document.body.appendChild(n);setTimeout(()=>{n.style.transform='translateX(0)';},10);setTimeout(()=>{n.style.transform='translateX(100%)';setTimeout(()=>{n.remove();},300);},3000);}

// Initialize
document.addEventListener('DOMContentLoaded',()=>{updateCartCount();});

// Lazy Loading for Images
document.addEventListener('DOMContentLoaded',()=>{const images=document.querySelectorAll('img[data-src]');const imageObserver=new IntersectionObserver((entries,observer)=>{entries.forEach(entry=>{if(entry.isIntersecting){const img=entry.target;img.src=img.dataset.src;img.removeAttribute('data-src');observer.unobserve(img);}});});images.forEach(img=>{imageObserver.observe(img);});});