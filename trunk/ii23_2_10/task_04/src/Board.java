import lombok.Getter;
import lombok.Setter;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

@Getter
@Setter
public class Board {

	private int size;
	private int score;
	private int emptyTiles;
	private int initTiles = 2;
	private boolean gameover = false;
	private String wonOrLost;
	private boolean genNewTile = false;
	private List<List<Tile>> tiles;

	private int moveCount = 0;
	private boolean bonusAvailable = false;


	public Board(int size) {
		super();
		this.size = size;
		this.emptyTiles = this.size * this.size;
		this.tiles = new ArrayList<>();

		start();
	}


	private void initialize() {
		for (int row = 0; row < this.size; row++) {
			tiles.add(new ArrayList<Tile>());
			for (int col = 0; col < this.size; col++) {
				tiles.get(row).add(new Tile());
			}
		}
	}
	
	private void start() {
		Game.CONTROLS.bind();
		initialize();
		genInitTiles();
	}

	public Tile getTileAt(int row, int col) {
		return tiles.get(row).get(col);
	}

	public void setTileAt(int row, int col, Tile t) {
		tiles.get(row).set(col, t);
	}

	public void remTileAt(int row, int col) {
		tiles.get(row).remove(col);
	}

	private List<Tile> addEmptyTilesFirst(List<Tile> merged) {
		for (int k = merged.size(); k < size; k++) {
			merged.add(0, new Tile());
		}
		return merged;
	}

	private List<Tile> addEmptyTilesLast(List<Tile> merged) { // boolean last/first
		for (int k = merged.size(); k < size; k++) {
			merged.add(k, new Tile());
		}
		return merged;
	}

	private List<Tile> removeEmptyTilesRows(int row) {

		List<Tile> moved = new ArrayList<>();

		for (int col = 0; col < size; col++) {
			if (!getTileAt(row, col).isEmpty()) { // NOT empty
				moved.add(getTileAt(row, col));
			}
		}

		return moved;
	}

	private List<Tile> removeEmptyTilesCols(int row) {

		List<Tile> moved = new ArrayList<>();

		for (int col = 0; col < size; col++) {
			if (!getTileAt(col, row).isEmpty()) { // NOT empty
				moved.add(getTileAt(col, row));
			}
		}

		return moved;
	}

	private List<Tile> setRowToBoard(List<Tile> moved, int row) {
		for (int col = 0; col < tiles.size(); col++) {
			if (moved.get(col).hasMoved(row, col)) {
				genNewTile = true;
			}
			setTileAt(row, col, moved.get(col));
		}

		return moved;
	}

	private List<Tile> setColToBoard(List<Tile> moved, int row) {
		for (int col = 0; col < tiles.size(); col++) {
			if (moved.get(col).hasMoved(col, row)) {
				genNewTile = true;
			}			
			setTileAt(col, row, moved.get(col));
		}

		return moved;
	}

	public void moveUp() {

		List<Tile> moved;

		for (int row = 0; row < size; row++) {

			moved = removeEmptyTilesCols(row);
			moved = mergeTiles(moved);
			moved = addEmptyTilesLast(moved);
			moved = setColToBoard(moved, row);

		}

	}

	public void moveDown() {

		List<Tile> moved;

		for (int row = 0; row < size; row++) {

			moved = removeEmptyTilesCols(row);
			moved = mergeTiles(moved);
			moved = addEmptyTilesFirst(moved);
			moved = setColToBoard(moved, row);

		}
		
	}

	public void moveLeft() {

		List<Tile> moved;

		for (int row = 0; row < size; row++) {

			moved = removeEmptyTilesRows(row);
			moved = mergeTiles(moved);
			moved = addEmptyTilesLast(moved);
			moved = setRowToBoard(moved, row);

		}
		
	}

	public void moveRight() {
		
		List<Tile> moved;
		
		for (int row = 0; row < size; row++) {

			moved = removeEmptyTilesRows(row);
			moved = mergeTiles(moved);
			moved = addEmptyTilesFirst(moved);
			moved = setRowToBoard(moved, row);

		}
		
	}

	private boolean isFull() {
		return emptyTiles == 0;
	}
	
	private boolean isMovePossible() {
		for (int row = 0; row < size; row++) {
			for (int col = 0; col < size - 1; col++) {
				if (getTileAt(row, col).getValue() == getTileAt(row, col + 1).getValue()) {
					return true;
				}
			}
		}
		
		for (int row = 0; row < size - 1; row++) {
			for (int col = 0; col < size; col++) {
				if (getTileAt(col, row).getValue() == getTileAt(col, row + 1).getValue()) {
					return true;
				}
			}
		}
		return false;
	}

	private void genInitTiles() {
		for (int i = 0; i < initTiles; i++) {
			genNewTile = true;
			newRandomTile();
		}
	}

	protected void show() {
		for (int i = 0; i < 2; ++i) System.out.println();
		System.out.println("SCORE: " + score);
		for (int i = 0; i < tiles.size(); i++) {
			for (int j = 0; j < tiles.get(i).size(); j++) {
				System.out.format("%-5d", getTileAt(i, j).getValue());
			}
			System.out.println();
		}
	}


	private void newRandomTile() {
		if (genNewTile) {
			int row, col;
			int value;

			double rand = Math.random();
			// && rand < 0.2
			if (bonusAvailable) {
				value = -1 - (int)(Math.random() * 3);
				bonusAvailable = false;
			} else if (rand < 0.9) {
				value = 2;
			} else {
				value = 4;
			}

			do {
				row = (int)(Math.random() * size);
				col = (int)(Math.random() * size);
			} while (getTileAt(row, col).getValue() != 0);

			setTileAt(row, col, new Tile(value, row, col));
			emptyTiles--;
			genNewTile = false;
		}
	}


	private List<Tile> mergeTiles(List<Tile> sequence) {
		for (int l = 0; l < sequence.size() - 1; l++) {
			Tile current = sequence.get(l);
			Tile next = sequence.get(l + 1);

			if (current.isUniversal() || next.isUniversal()) {
				int newValue = current.isUniversal() ? next.getValue() * 2 : current.getValue() * 2;
				if (newValue == 2048) {
					gameover = true;
				}
				score += newValue;
				sequence.set(l, new Tile(newValue));
				sequence.remove(l + 1);
				genNewTile = true;
				emptyTiles++;
				continue;
			}

			if (current.getValue() == next.getValue()) {
				int value;
				if ((value = current.merging()) == 2048) {
					gameover = true;
				}
				score += value;
				sequence.remove(l + 1);
				genNewTile = true;
				emptyTiles++;
			}
		}
		return sequence;
	}

	public void processSpecialTiles() {
		for (int row = 0; row < size; row++) {
			for (int col = 0; col < size; col++) {
				Tile tile = getTileAt(row, col);

				if (tile.isRemover()) {
					removeRandomAdjacent(row, col);
					setTileAt(row, col, new Tile(0));
					emptyTiles++;
				}
				else if (tile.isShuffler()) {
					setTileAt(row, col, new Tile(0));
					shuffleTiles();
					emptyTiles++;
					return;
				}
			}
		}
	}
	private void removeRandomAdjacent(int row, int col) {
		Game.GRID.selectingForRemoval = true;
	}


	public void shuffleTiles() {
		List<Tile> nonEmptyTiles = new ArrayList<>();
		for (int row = 0; row < size; row++) {
			for (int col = 0; col < size; col++) {
				Tile tile = getTileAt(row, col);
				if (!tile.isEmpty()) {
					nonEmptyTiles.add(tile);
					setTileAt(row, col, new Tile(0));
				}
			}
		}

		Collections.shuffle(nonEmptyTiles);

		for (Tile tile : nonEmptyTiles) {
			int row, col;
			do {
				row = (int)(Math.random() * size);
				col = (int)(Math.random() * size);
			} while (!getTileAt(row, col).isEmpty());

			setTileAt(row, col, new Tile(tile.getValue(), row, col));
			emptyTiles--;
		}
	}

	public void isGameOver() {
		processSpecialTiles();

		if (gameover) {
			setWonOrLost("WON");
		} else {
			if (isFull()) {
				if (!isMovePossible()) {
					setWonOrLost("LOST");
				}
			} else {
				moveCount++;

				if (moveCount % 5 == 0) {
					bonusAvailable = true;
				}

				newRandomTile();
			}
		}
	}
}