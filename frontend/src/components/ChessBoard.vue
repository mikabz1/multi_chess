<template>
  <div class="board-wrap">
    <div class="board-shell" :class="{ flipped: yourColor === 'black' }">
      <div class="rank-labels rank-labels-left">
        <span v-for="rank in displayRanks" :key="`left-${rank}`">{{ rank }}</span>
      </div>

      <div class="board-area">
        <div class="file-labels file-labels-top">
          <span v-for="file in displayFiles" :key="`top-${file}`">{{ file }}</span>
        </div>

        <div class="board">
          <button
            v-for="square in displayedSquares"
            :key="square.name"
            class="square"
            :class="[
              square.color,
              {
                selected: selected === square.name,
                last: lastMoveSquares.includes(square.name),
                legal: legalTargetSquares.includes(square.name),
                capture: legalCaptureSquares.includes(square.name),
              },
            ]"
            @click="onSquareClick(square.name)"
          >
            <span
              v-if="square.piece"
              class="piece"
              :class="square.pieceColor === 'w' ? 'white-piece' : 'black-piece'"
            >
              {{ square.piece }}
            </span>
            <span v-if="legalTargetSquares.includes(square.name)" class="legal-dot"></span>
          </button>
        </div>

        <div class="file-labels file-labels-bottom">
          <span v-for="file in displayFiles" :key="`bottom-${file}`">{{ file }}</span>
        </div>
      </div>

      <div class="rank-labels rank-labels-right">
        <span v-for="rank in displayRanks" :key="`right-${rank}`">{{ rank }}</span>
      </div>
    </div>

    <p class="hint">Click a piece to see legal moves. Promotion defaults to queen.</p>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Chess } from 'chess.js'

const props = defineProps({
  fen: { type: String, required: true },
  yourColor: { type: String, default: 'white' },
  lastMove: { type: String, default: '' },
})
const emit = defineEmits(['move'])

const selected = ref(null)
const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
const ranks = [8, 7, 6, 5, 4, 3, 2, 1]

// Filled glyphs are used for both colors. CSS paints white pieces truly white.
const pieceMap = {
  p: '♟', n: '♞', b: '♝', r: '♜', q: '♛', k: '♚',
}

const chess = computed(() => new Chess(props.fen))
const lastMoveSquares = computed(() => props.lastMove ? [props.lastMove.slice(0, 2), props.lastMove.slice(2, 4)] : [])

const displayFiles = computed(() => props.yourColor === 'black' ? [...files].reverse() : files)
const displayRanks = computed(() => props.yourColor === 'black' ? [...ranks].reverse() : ranks)

const squares = computed(() => {
  const result = []
  for (let rank = 8; rank >= 1; rank--) {
    for (let fileIndex = 0; fileIndex < 8; fileIndex++) {
      const file = files[fileIndex]
      const name = `${file}${rank}`
      const piece = chess.value.get(name)
      result.push({
        name,
        color: (rank + fileIndex) % 2 !== 0 ? 'dark' : 'light',
        piece: piece ? pieceMap[piece.type] : '',
        pieceColor: piece?.color || null,
      })
    }
  }
  return result
})

const displayedSquares = computed(() => {
  if (props.yourColor === 'black') return [...squares.value].reverse()
  return squares.value
})

const legalMoves = computed(() => {
  if (!selected.value) return []
  try {
    return chess.value.moves({ square: selected.value, verbose: true })
  } catch {
    return []
  }
})

const legalTargetSquares = computed(() => legalMoves.value.map((move) => move.to))
const legalCaptureSquares = computed(() => legalMoves.value.filter((move) => move.captured).map((move) => move.to))

watch(() => props.fen, () => { selected.value = null })

function onSquareClick(square) {
  const piece = chess.value.get(square)
  const myColor = props.yourColor === 'white' ? 'w' : 'b'

  if (!selected.value) {
    if (!piece || piece.color !== myColor) return
    selected.value = square
    return
  }

  if (selected.value === square) {
    selected.value = null
    return
  }

  // Clicking another piece of the same color changes the selected piece.
  const selectedPiece = chess.value.get(selected.value)
  if (piece && selectedPiece && piece.color === selectedPiece.color && piece.color === myColor) {
    selected.value = square
    return
  }

  if (!legalTargetSquares.value.includes(square)) {
    return
  }

  let move = `${selected.value}${square}`
  const movingPiece = chess.value.get(selected.value)
  const targetRank = square[1]
  if (movingPiece?.type === 'p' && (targetRank === '8' || targetRank === '1')) {
    move += 'q'
  }
  emit('move', move)
  selected.value = null
}
</script>
