describe('TicTacToe - Draw Scenario (Cypress)', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000');
  });

  it('should detect draw when all cells filled without winner - pattern 1', () => {
    const moves = [0, 2, 1, 3, 5, 4, 6, 7, 8];

    moves.forEach(cellIndex => {
      cy.get(`[data-testid="cell-${cellIndex}"]`).click();
    });

    cy.get('[data-testid="game-status"]').should('match', /draw|tie/i);
    
    cy.get('[data-testid^="cell-"]').should('have.length', 9);
    
    for (let i = 0; i < 9; i++) {
      cy.get(`[data-testid="cell-${i}"]`).should('not.be.empty');
    }
  });

  it('should detect draw when all cells filled without winner - pattern 2', () => {
    const moves = [1, 0, 2, 5, 3, 6, 4, 7, 8];

    moves.forEach(cellIndex => {
      cy.get(`[data-testid="cell-${cellIndex}"]`).click();
    });

    cy.get('[data-testid="game-status"]').should('match', /draw|tie/i);
  });

  it('should disable all cells after draw', () => {
    const moves = [0, 2, 1, 3, 5, 4, 6, 7, 8];

    moves.forEach(cellIndex => {
      cy.get(`[data-testid="cell-${cellIndex}"]`).click();
    });

    for (let i = 0; i < 9; i++) {
      cy.get(`[data-testid="cell-${i}"]`).should('be.disabled');
    }
  });

  it('should allow restart after draw', () => {
    const moves = [0, 2, 1, 3, 5, 4, 6, 7, 8];

    moves.forEach(cellIndex => {
      cy.get(`[data-testid="cell-${cellIndex}"]`).click();
    });

    cy.get('[data-testid="game-status"]').should('match', /draw|tie/i);
    cy.get('[data-testid="restart-button"]').should('be.visible').click();

    for (let i = 0; i < 9; i++) {
      cy.get(`[data-testid="cell-${i}"]`).should('be.empty').and('be.enabled');
    }

    cy.get('[data-testid="game-status"]').should('match', /X.*turn|next.*X/i);
  });

  it('should show correct player turns during draw scenario', () => {
    const moves = [
      { cell: 0, expectedNext: /O.*turn|next.*O/i },
      { cell: 2, expectedNext: /X.*turn|next.*X/i },
      { cell: 1, expectedNext: /O.*turn|next.*O/i },
      { cell: 3, expectedNext: /X.*turn|next.*X/i },
      { cell: 5, expectedNext: /O.*turn|next.*O/i },
      { cell: 4, expectedNext: /X.*turn|next.*X/i },
      { cell: 6, expectedNext: /O.*turn|next.*O/i },
      { cell: 7, expectedNext: /X.*turn|next.*X/i }
    ];

    moves.forEach(move => {
      cy.get(`[data-testid="cell-${move.cell}"]`).click();
      cy.get('[data-testid="game-status"]').should('match', move.expectedNext);
    });

    cy.get('[data-testid="cell-8"]').click();
    cy.get('[data-testid="game-status"]').should('match', /draw|tie/i);
  });

  it('should not allow clicking filled cells during draw scenario', () => {
    cy.get('[data-testid="cell-0"]').click();
    cy.get('[data-testid="cell-0"]').should('contain.text', 'X');

    cy.get('[data-testid="cell-0"]').click();
    cy.get('[data-testid="cell-0"]').should('contain.text', 'X').and('not.contain.text', 'O');
  });

  it('should maintain game state consistency throughout draw', () => {
    const moves = [0, 2, 1, 3, 5, 4, 6, 7, 8];
    const expectedBoard = ['X', 'X', 'O', 'O', 'O', 'X', 'X', 'O', 'X'];

    moves.forEach(cellIndex => {
      cy.get(`[data-testid="cell-${cellIndex}"]`).click();
    });

    expectedBoard.forEach((mark, index) => {
      cy.get(`[data-testid="cell-${index}"]`).should('contain.text', mark);
    });

    cy.get('[data-testid="game-status"]').should('match', /draw|tie/i);
  });

  it('should handle multiple draw games in sequence', () => {
    const moves = [0, 2, 1, 3, 5, 4, 6, 7, 8];

    for (let game = 0; game < 3; game++) {
      moves.forEach(cellIndex => {
        cy.get(`[data-testid="cell-${cellIndex}"]`).click();
      });

      cy.get('[data-testid="game-status"]').should('match', /draw|tie/i);
      
      if (game < 2) {
        cy.get('[data-testid="restart-button"]').click();
      }
    }
  });
});