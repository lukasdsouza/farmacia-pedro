-- Base de Dados Ficticia - Farmacia (MySQL)

-- 1) Tabela: produtos
CREATE TABLE produtos (
    id_produto INT PRIMARY KEY AUTO_INCREMENT,
    sku VARCHAR(50),
    nome VARCHAR(150),
    categoria VARCHAR(100),
    status ENUM('ATIVO', 'INATIVO'),
    preco_venda DECIMAL(10,2),
    custo_medio DECIMAL(10,2),
    data_cadastro DATE
);

INSERT INTO produtos VALUES
(1,'MED001','Dipirona 500mg','Analgesico','ATIVO',12.90,5.20,'2023-01-10'),
(2,'MED002','Paracetamol 750mg','Analgesico','ATIVO',18.50,7.00,'2023-02-05'),
(3,'MED003','Amoxicilina 500mg','Antibiotico','ATIVO',42.00,28.00,'2023-03-15'),
(4,'HIG001','Alcool Gel 70%','Higiene','ATIVO',9.90,3.50,'2022-11-20'),
(5,'HIG002','Mascara Descartavel','Higiene','ATIVO',2.50,0.80,'2022-10-01'),
(6,'SUP001','Vitamina C 1g','Suplemento','ATIVO',39.90,18.00,'2023-04-12');

-- 2) Tabela: estoque
CREATE TABLE estoque (
    id_estoque INT PRIMARY KEY AUTO_INCREMENT,
    id_produto INT,
    filial VARCHAR(100),
    quantidade INT,
    reservado INT,
    FOREIGN KEY (id_produto) REFERENCES produtos(id_produto)
);

INSERT INTO estoque VALUES
(1,1,'Centro',120,10),
(2,2,'Centro',60,5),
(3,3,'Centro',15,2),
(4,4,'Centro',300,20),
(5,5,'Centro',500,50),
(6,6,'Centro',8,1);

-- 3) Tabela: vendas
CREATE TABLE vendas (
    id_venda INT PRIMARY KEY AUTO_INCREMENT,
    data_venda DATE,
    filial VARCHAR(100),
    vendedor VARCHAR(100),
    valor_total DECIMAL(10,2)
);

INSERT INTO vendas VALUES
(1,'2025-12-01','Centro','Joao',125.80),
(2,'2025-12-05','Centro','Maria',89.50),
(3,'2026-01-10','Centro','Carlos',42.00),
(4,'2026-01-15','Centro','Joao',18.50);

-- 4) Tabela: itens_venda
CREATE TABLE itens_venda (
    id_item INT PRIMARY KEY AUTO_INCREMENT,
    id_venda INT,
    id_produto INT,
    quantidade INT,
    preco_unitario DECIMAL(10,2),
    FOREIGN KEY (id_venda) REFERENCES vendas(id_venda),
    FOREIGN KEY (id_produto) REFERENCES produtos(id_produto)
);

INSERT INTO itens_venda VALUES
(1,1,1,5,12.90),
(2,1,4,3,9.90),
(3,2,2,2,18.50),
(4,3,3,1,42.00),
(5,4,2,1,18.50);

-- 5) View pronta para IA
CREATE VIEW vw_produto_analise AS
SELECT
    p.id_produto,
    p.nome,
    p.categoria,
    p.preco_venda,
    p.custo_medio,
    ROUND(((p.preco_venda - p.custo_medio) / p.custo_medio) * 100,2) AS markup_percentual,
    e.quantidade,
    e.reservado
FROM produtos p
JOIN estoque e ON p.id_produto = e.id_produto;

-- 6) Consultas exemplo para IA
-- Produtos com markup acima de 110%
SELECT * FROM vw_produto_analise
WHERE markup_percentual > 110;

-- Produtos sem venda nos ultimos 60 dias
SELECT p.id_produto, p.nome
FROM produtos p
LEFT JOIN itens_venda iv ON p.id_produto = iv.id_produto
LEFT JOIN vendas v ON iv.id_venda = v.id_venda
GROUP BY p.id_produto
HAVING MAX(v.data_venda) < DATE_SUB(CURDATE(), INTERVAL 60 DAY)
   OR MAX(v.data_venda) IS NULL;

-- Estoque baixo
SELECT nome, quantidade
FROM vw_produto_analise
WHERE quantidade < 10;
