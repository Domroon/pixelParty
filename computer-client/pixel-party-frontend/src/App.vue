<script setup>

</script>

<template>
<div>
  <h1>LED Matrix</h1>
  <h2>Status</h2>
  <div class="status"><div class="circle online"></div><div class="name">Computer Client</div></div>
  <div class="status"><div class="circle offline"></div><div class="name">Matrix Client</div></div>
  <h2>Was willst Du Anzeigen?</h2>
  <button>Text</button>
  <button>Animation</button>
  <button>Bild</button>
  <button>Wetter</button>
  <button>Nachrichten</button>
</div>
</template>

<style scoped>
h1 {
  font-size: 5rem;
  color:rgb(10, 224, 28);
}

h2 {
  font-size: 2rem;
  color: rgb(0, 132, 255);
}

.status {
  display: flex;
  font-size: 1.5rem;
}

.circle {
  height: 20px;
  width: 20px;
  border-radius: 10px;
  margin: 1rem;
}

.online {
  background-color: green;
}

.offline {
  background-color: red;
}

.name {
  margin-top: .4rem;
}

button {
  background-color: transparent;
  color: orange;
  border-color: orange;
  font-size: 2rem;
  border-radius: 10px;
  padding: 1rem;
  margin: 1rem;
  cursor: pointer;
}

button:hover {
  background: rgba(255, 166, 0, 0.377);
  color: black;
  transition: all 0.2s;
}
</style>
