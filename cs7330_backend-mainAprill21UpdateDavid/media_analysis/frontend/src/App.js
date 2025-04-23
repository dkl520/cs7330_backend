import React, { useState } from 'react';
import './App.css';

function App() {
  const [view, setView] = useState('post');
  const [result, setResult] = useState([]);
  const [name, setName] = useState('');
  const [postParams, setPostParams] = useState({
    media: '',
    start_date: '',
    end_date: '',
    username: '',
    author: '',
  });

  const query = new URLSearchParams(postParams).toString();
  const handlePostSearch = () => {
    fetch(`http://127.0.0.1:8000/api/query/post/?${query}`)
      .then(response => response.json())
      .then(data => setResult(data))
      .catch(error => console.error('Error fetching data:', error));
  };

  const handleExperimentSearch = () => {
    fetch(`http://127.0.0.1:8000/api/query/experiment/?name=${name}`)
      .then(response => response.json())
      .then(data => setResult(data))
      .catch(error => console.error('Error fetching data:', error));
  };
  
  return (
    <div className="App">
      <h1>Social Media Analysis</h1>
      <div className="button-bar">
        <button onClick={() => setView('post')}>Post</button>
        <button onClick={() => setView('experiment')}>Experiment</button>
      </div>

      
        {view === 'post' && (
          <PostView
          data={result}
          params={postParams}
          setParams={setPostParams}
          handleSearch={handlePostSearch}
  />
)}
        {view === 'experiment' && (
          <ExperimentView
          data={result}
          name={name}
          setName={setName}
          handleSearch={handleExperimentSearch}
  />
)}
     
    </div>
  );
}

function PostView({ data, params, setParams, handleSearch }) {
  return (
    <div>
    <div className = "search-bar">
        <input
          type = "text"
          placeholder = 'media'
          value={params.media}
          onChange={(e) => setParams((prev) => ( {...prev, media : e.target.value}))}
        />
        <input
          type = "text"
          placeholder = 'Start date'
          value={params.start_date}
          onChange={(e) => setParams((prev) => ( {...prev, start_date : e.target.value}))}
        />
        <input
          type = "text"
          placeholder = 'End Date'
          value={params.end_date}
          onChange={(e) => setParams((prev) => ( {...prev, end_date : e.target.value}))}
        />
        <input
          type = "text"
          placeholder = 'username'
          value={params.username}
          onChange={(e) => setParams((prev) => ( {...prev, username : e.target.value}))}
        />
        <input
          type = "text"
          placeholder = 'author'
          value={params.author}
          onChange={(e) => setParams((prev) => ( {...prev, author : e.target.value}))}
        />
        <button onClick = {handleSearch}>Search</button>
      </div>
      <h2>Post List</h2>
    <div className="table-container">
    <table >
      <thead>
        <tr>
          <th>content</th>
          <th>media</th>
          <th>username</th>
          <th>post_time</th>
          <th>experiments</th>
        </tr>
      </thead>
      <tbody>
        {data.map((r, index) => (
          <tr key={index}>
            <td>{r.content}</td>
            <td>{r.media}</td>
            <td>{r.username}</td>
            <td>{r.time}</td>
            <td>{r.experiments.join(', ')}</td>
          </tr>
        ))}
      </tbody>
    </table>
    </div>
    </div>
  );
}

function ExperimentView({ data, name, setName, handleSearch }) {
  return (
    <div>
      <div className = "search-bar">
        <input
          type = "text"
          placeholder = 'name'
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <button onClick = {handleSearch}>Search</button>
        </div>
    <h2>Experiment List</h2>
    <div className="table-container">
    <table>
      <thead>
        <tr>
          <th>post_id</th>
          <th>username</th>
          <th>media</th>
          <th>content</th>
          <th>post_time</th>
          <th>city</th>
          <th>state</th>
          <th>country</th>
          <th>likes</th>
          <th>dislikes</th>
          <th>has_multimedia</th>
          <th>field</th>
          <th>value</th>
        </tr>
      </thead>
      <tbody>
      {data.posts && data.posts.map((r, index) => (
          <tr key={index}>
            <td>{r.post_id}</td>
            <td>{r.username}</td>
            <td>{r.media}</td>
            <td>{r.content}</td>
            <td>{r.time}</td>
            <td>{r.city}</td>
            <td>{r.state}</td>
            <td>{r.country}</td>
            <td>{r.likes}</td>
            <td>{r.dislikes}</td>
            <td>{r.has_multimedia? 'Yes':'No'}</td>
            <td>{r.field}</td>
            <td>{r.value.join(', ')}</td>
          </tr>
        ))}
      </tbody>
    </table>
    </div>
    <h2 style={{ marginTop: '200px' }}>Field Percentages</h2>
    <div className="table-container">
  <table >
  <thead>
    <tr>
      <th>Field</th>
      <th>Percentage (%)</th>
    </tr>
  </thead>
  <tbody>
    {data.percentages &&
      Object.entries(data.percentages).map(([field, percent]) => (
        <tr key={field}>
          <td>{field}</td>
          <td>{percent}%</td>
        </tr>
      ))}
  </tbody>
</table>
</div>
    </div>
  );
}
  export default App;