import React, { useState } from 'react';

const GeneratePlaylistButton = () => {
  const [artists, setArtists] = useState(null);
  const [error, setError] = useState(null);

  const fetchArtists = async () => {
    try {
      // Step 1: Check if the user is logged in
      const loginResponse = await fetch('http://127.0.0.1:5000/is_logged_in');
      const loginStatus = await loginResponse.json();

      if (!loginStatus.logged_in) {
        // Step 2: If not logged in, redirect to Spotify login
        window.location.href = 'http://127.0.0.1:5000/login';
        return;
      }

      // Step 3: If logged in, fetch the artists
      const response = await fetch('http://127.0.0.1:5000/artistsYouLike');

      if (!response.ok) {
        throw new Error('Failed to fetch artists');
      }

      const artists = await response.json();
      setArtists(artists); // Update the state to display artists
    } catch (error) {
      console.error('Error fetching artists:', error);
      setError('An error occurred while fetching artists.');
    }
  };

  return (
    <div>
      <button onClick={fetchArtists} className="generate-playlist">
        Generate Playlist
      </button>

      {error && <p>{error}</p>}

      {artists && (
        <div>
          <h3>Artists:</h3>
          <ul>
            {artists.map((artist, index) => (
              <li key={index}>{artist.name}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default GeneratePlaylistButton;
