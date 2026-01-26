const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Candidatura = sequelize.define('Candidatura', {
    id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
    },
    userId: {
        type: DataTypes.INTEGER,
        allowNull: false,
        references: {
            model: 'Users',
            key: 'id'
        }
    },
    oportunidadeId: {
        type: DataTypes.INTEGER,
        allowNull: false,
        references: {
            model: 'Oportunidades',
            key: 'id'
        }
    },
    status: {
        type: DataTypes.ENUM('Enviada', 'Em Análise', 'Aceita', 'Rejeitada'),
        defaultValue: 'Enviada'
    },
    dataCandidatura: {
        type: DataTypes.DATE,
        defaultValue: DataTypes.NOW
    },
    observacoes: {
        type: DataTypes.TEXT
    }
});

module.exports = Candidatura;
