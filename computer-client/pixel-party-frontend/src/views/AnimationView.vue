<script setup>
import { ref } from 'vue'
import axios  from 'axios'

const selected = ref('')

const sendScrollText = (text) => {
  axios.post('http://127.0.0.1:8000/pixel-master/scroll-text',
    {
      'text': text
    },
    {
      headers: {
        'accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })
    .then(response => console.log(response))
}

const sendAni = (animation) => {
  axios.post(`http://127.0.0.1:8000/pixel-master/animation?ani_type=${animation}`,
    {
      headers: {
        'accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })
    .then(response => console.log(response))
}

const send = () => {
  if (selected.value === "Pixelrauschen") {
    sendAni("random_colors")
  }
  else if (selected.value === "Zufälliges Blinken") {
    sendAni("random_color_flash")
  }
}

</script>

<template>
  <main>
    <div class="input-field">
      <h1>Bitte Animation wählen</h1>
      <div>Deine Auswahl: {{ selected }}</div>
      <select v-model="selected">
        <option disabled value="">Auswählen</option>
        <option>Zufälliges Blinken</option>
        <option>Pixelrauschen</option>
      </select>
      <button v-on:click="send" class="btn">Senden</button>
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

