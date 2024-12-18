// script.js
function toggleImage() {
  const modal = document.getElementById('imageModal');

  if (modal.style.display === 'flex') {
    modal.style.opacity = '0';
    setTimeout(() => {
      modal.style.display = 'none';
    }, 500);
  } else {
    modal.style.display = 'flex';
    setTimeout(() => {
      modal.style.opacity = '1';
    }, 10);
  }
}

window.onclick = function(event) {
  const modal = document.getElementById('imageModal');
  if (event.target === modal) {
    toggleImage();
  }
};

function openImage() {
  const modal = document.getElementById('imageModal');
  modal.style.display = 'flex';
  modal.style.opacity = '1';
  console.log('ffff')
}

function closeImage() {
  const modal = document.getElementById('imageModal');
  modal.style.opacity = '0';
  setTimeout(() => {
    modal.style.display = 'none';
  }, 500);
}

function updateHeader() {
  const header = document.querySelector('.count');

  if (window.innerWidth > 600) {
    header.textContent = 'Количество';
  } else {
    header.textContent = 'Кол-во';
  }
}

updateHeader();

window.addEventListener('resize', updateHeader);

const likeButton = document.getElementById('like-button');
const dislikeButton = document.getElementById('dislike-button');

function updateButtonImages() {
  const likeImage = likeButton.querySelector('img');
  const dislikeImage = dislikeButton.querySelector('img');

  if (likeButton.classList.contains('active')) {
    likeImage.src = likeButton.dataset.likeImg;   // Получаем путь из data-like-img
    dislikeImage.src = dislikeButton.dataset.dislikeImg; // Получаем путь из data-dislike-img
  } else {
    likeImage.src = dislikeButton.dataset.dislikeImg; // Получаем путь из data-dislike-img
    dislikeImage.src = likeButton.dataset.likeImg;   // Получаем путь из data-like-img
  }
}

likeButton.addEventListener('click', function() {
  setActive(likeButton);
  rateOrder('{{ order.uuid }}', true);
});

dislikeButton.addEventListener('click', function() {
  setActive(dislikeButton);
  rateOrder('{{ order.uuid }}', false);
});
