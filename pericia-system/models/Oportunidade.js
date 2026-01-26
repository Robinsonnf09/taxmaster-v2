const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Oportunidade = sequelize.define('Oportunidade', {
    id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
    },
    tribunal: {
        type: DataTypes.STRING,
        allowNull: false
    },
    processo: {
        type: DataTypes.STRING,
        allowNull: false,
        unique: true
    },
    especialidade: {
        type: DataTypes.STRING,
        allowNull: false
    },
    valorCausa: {
        type: DataTypes.DECIMAL(15, 2),
        defaultValue: 0
    },
    honorariosEstimados: {
        type: DataTypes.DECIMAL(15, 2),
        defaultValue: 0
    },
    horasEstimadas: {
        type: DataTypes.INTEGER,
        defaultValue: 0
    },
    complexidade: {
        type: DataTypes.DECIMAL(3, 1),
        defaultValue: 1.0
    },
    prazo: {
        type: DataTypes.DATE
    },
    score: {
        type: DataTypes.INTEGER,
        defaultValue: 0
    },
    status: {
        type: DataTypes.ENUM('Nova', 'Candidatado', 'Em Análise', 'Contratado', 'Rejeitado', 'Concluído'),
        defaultValue: 'Nova'
    },
    urgente: {
        type: DataTypes.BOOLEAN,
        defaultValue: false
    },
    dataDeteccao: {
        type: DataTypes.DATE,
        defaultValue: DataTypes.NOW
    },
    observacoes: {
        type: DataTypes.TEXT
    }
});

module.exports = Oportunidade;
