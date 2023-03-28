<script setup>
import { ref } from 'vue'
import axios  from 'axios'

const selected_source_id = ref('')

const sendSourceID = () => {
  console.log()
  axios.post(`http://127.0.0.1:8000/pixel-master/news`,
    { 
      'text': selected_source_id.value
    },
    {
      headers: {
        'accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })
    .then(response => console.log(response))
}

const send = () => {
  if (selected_source_id.value === "T3n") {
    sendSourceID("t3n")
  }
  else if (selected_source_id.value === "Bild") {
    sendSourceID("bild")
  }
  else if (selected_source_id.value === "Der Tagesspiegel") {
    sendSourceID("der-tagesspiegel")
  }
  else if (selected_source_id.value === "Die Zeit") {
    sendSourceID("die-zeit")
  }
  else if (selected_source_id.value === "Focus") {
    sendSourceID("focus")
  }
  else if (selected_source_id.value === "Gruenderszene") {
    sendSourceID("gruenderszene")
  }
  else if (selected_source_id.value === "Handelsblatt") {
    sendSourceID("handelsblatt")
  }
  else if (selected_source_id.value === "Spiegel Online") {
    sendSourceID("spiegel-online")
  }
  else if (selected_source_id.value === "Wired.de") {
    sendSourceID("wired-de")
  }
  else if (selected_source_id.value === "Wirtschafts Woche") {
    sendSourceID("wirtschafts-woche")
  }
}
</script>

<template>
  <main>
    <div class="input-field">
      <h1>Bitte Nachrichtenquelle wählen</h1>
      <div>Deine Auswahl: {{ selected_source_id }}</div>
      <select v-model="selected_source_id">
        <option disabled value="">Auswählen</option>
        <option>T3n</option>
        <option>Bild</option>
        <option>Der Tagesspiegel</option>
        <option>Die Zeit</option>
        <option>Focus</option>
        <option>Gruenderszene</option>
        <option>Handelsblatt</option>
        <option>Wired.de</option>
        <option>Spiegel Online</option>
        <option>Wirtschafts Woche</option>
      </select>
      <button v-on:click="sendSourceID" class="btn">Senden</button>
    </div>
  </main>
  
</template>

<style>
@media (min-width: 1024px) {
  main {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
}

input {
  height: 4rem;
}

.btn {
  background-color: transparent;
  color: orange;
  border-color: orange;
  font-size: 2rem;
  border-radius: 10px;
  padding: 1rem;
  margin: 1rem;
  cursor: pointer;
}

 /* Dropdown Button */
 .dropbtn {
  background-color: #04AA6D;
  color: white;
  padding: 16px;
  font-size: 16px;
  border: none;
}

/* The container <div> - needed to position the dropdown content */
.dropdown {
  position: relative;
  display: inline-block;
}

/* Dropdown Content (Hidden by Default) */
.dropdown-content {
  display: none;
  position: absolute;
  background-color: #f1f1f1;
  min-width: 160px;
  box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
  z-index: 1;
}

/* Links inside the dropdown */
.dropdown-content a {
  color: black;
  padding: 12px 16px;
  text-decoration: none;
  display: block;
}

/* Change color of dropdown links on hover */
.dropdown-content a:hover {background-color: #ddd;}

/* Show the dropdown menu on hover */
.dropdown:hover .dropdown-content {display: block;}

/* Change the background color of the dropdown button when the dropdown content is shown */
.dropdown:hover .dropbtn {background-color: #3e8e41;} 
</style>

