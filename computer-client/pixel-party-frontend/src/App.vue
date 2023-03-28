<script setup>
  import { onMounted, ref} from 'vue';
  import axios  from 'axios'

  const status = ref('')
  const showRed = ref(false)

  const getStatus = () => {
    axios
      .get('http://127.0.0.1:8000/pixel-master/status')
      .then(response => {
        console.log(response.data)
        status.value = response.data
        console.log({"status": status.value})
        if(status.value === "offline") {
          showRed.value = true
        } else {
          showRed.value = false
        }
        
      })
  }

  onMounted(() => {
    console.log("log for first time")
    getStatus()
    setInterval(() => {
      console.log("logging")
      getStatus()
    }, 2000)
  })
</script>

<template>
  <div>
    <h1>LED Matrix</h1>
    <h2>Status</h2>
    <div class="status"><div class="circle online"></div><div class="name">Computer Client</div></div>
    <div class="status">
      <div v-if="showRed" class="circle offline"></div>
      <div v-else class="circle online"></div>
      <div class="name">Matrix Client</div>
    </div>
    <h2>Was willst Du Anzeigen?</h2>
    <div class="buttons">
      <router-link to="/text" class="btn">Text</router-link>
      <router-link to="/animation" class="btn">Animation</router-link>
      <router-link to="/picture" class="btn">Bild</router-link>
      <router-link to="/weather" class="btn">Wetter</router-link>
      <router-link to="/news" class="btn">Nachrichten</router-link>
    </div>
  </div>
  <div>
    <router-view></router-view>
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

#app {
  max-width: 100%;
  display: flex;
  justify-content: baseline;
  justify-content: space-between;
}

.status {
  display: flex;
  font-size: 1.5rem;
}

.buttons {
  display: flex;
  max-width: 100px;
  flex-wrap: wrap;
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

.btn {
  display: inline;
  background-color: transparent;
  color: orange;
  border-color: orange;
  font-size: 2rem;
  border-radius: 10px;
  padding: 1rem;
  margin: 1rem;
  cursor: pointer;
}

.btn:hover {
  background: rgba(255, 166, 0, 0.377);
  color: black;
  transition: all 0.2s;
}
</style>
