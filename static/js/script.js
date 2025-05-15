function handleMatch(profileId, liked) {
  const url = liked === true ? '/like/' : '/next/';

  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken(),
    },
    body: JSON.stringify({ profile_id: profileId })
  })
  .then(response => response.json())
  .then(data => {
    if (data.match) {
      alert("🎉 It's a match with " + data.match_with + "!");
    }
    document.getElementById('profile-section').innerHTML = data.next_profile_html;
  });
}

// Helper to get CSRF token from cookie
function getCSRFToken() {
  let csrfToken = null;
  document.cookie.split(';').forEach(cookie => {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrftoken') {
      csrfToken = decodeURIComponent(value);
    }
  });
  return csrfToken;
}


