(function () {
  const state = window.INITIAL_GAME;
  const grid = document.getElementById("grid");
  const form = document.getElementById("guess-form");
  const input = document.getElementById("guess-input");
  const errorMsg = document.getElementById("error-msg");
  const modalOverlay = document.getElementById("result-modal");
  const modalTitle = document.getElementById("modal-title");
  const modalText = document.getElementById("modal-text");
  const modalOk = document.getElementById("modal-ok");

  function renderGrid() {
    grid.innerHTML = "";
    for (let r = 0; r < state.max_guesses; r++) {
      const row = document.createElement("div");
      row.className = "grid-row";
      const guessRow = state.guesses[r];

      for (let c = 0; c < state.word_length; c++) {
        const cell = document.createElement("div");
        cell.className = "tile";
        if (guessRow) {
          cell.textContent = guessRow.guess[c];
          cell.classList.add("tile-" + guessRow.result[c]);
        }
        row.appendChild(cell);
      }
      grid.appendChild(row);
    }
  }

  function showModal(title, text) {
    modalTitle.textContent = title;
    modalText.textContent = text;
    modalOverlay.classList.remove("hidden");
  }

  if (modalOk) {
    modalOk.addEventListener("click", function () {
      modalOverlay.classList.add("hidden");
      window.location.href = "/play/";
    });
  }

  if (form) {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();
      errorMsg.textContent = "";
      const guess = input.value.trim().toUpperCase();

      if (guess.length !== state.word_length || !/^[A-Z]+$/.test(guess)) {
        errorMsg.textContent = `Enter exactly ${state.word_length} letters.`;
        return;
      }

      try {
        const res = await fetch("/play/guess", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ guess: guess }),
        });
        const data = await res.json();

        if (!res.ok) {
          errorMsg.textContent = data.error || "Something went wrong.";
          return;
        }

        state.guesses.push({ guess: data.guess, result: data.result });
        renderGrid();
        input.value = "";

        if (data.game_over) {
          input.disabled = true;
          form.querySelector("button").disabled = true;
          if (data.won) {
            showModal("Congratulations!", `You guessed the word "${data.answer}" correctly.`);
          } else {
            showModal("Better luck next time", `The word was "${data.answer}".`);
          }
        }
      } catch (err) {
        errorMsg.textContent = "Network error. Please try again.";
      }
    });
  }

  renderGrid();

  // If the game already ended (e.g. page refresh after a finished game),
  // reflect that in the UI without popping the modal again.
  if (state.status !== "in_progress") {
    input.disabled = true;
    form.querySelector("button").disabled = true;
  }
})();
