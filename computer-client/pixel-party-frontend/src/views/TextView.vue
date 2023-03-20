<template>
  <main>
    <h1>Bitte einen Text eingeben</h1>
    <input v-model="text">
    <button class="btn">Senden</button>
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
</style>
