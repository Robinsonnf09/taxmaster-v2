const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');
const bcrypt = require('bcryptjs');

const User = sequelize.define('User', {
    id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
    },
    nome: {
        type: DataTypes.STRING,
        allowNull: false
    },
    email: {
        type: DataTypes.STRING,
        allowNull: false,
        unique: true,
        validate: {
            isEmail: true
        }
    },
    senha: {
        type: DataTypes.STRING,
        allowNull: false
    },
    cpf: {
        type: DataTypes.STRING,
        unique: true
    },
    telefone: {
        type: DataTypes.STRING
    },
    especialidades: {
        type: DataTypes.ARRAY(DataTypes.STRING),
        defaultValue: []
    },
    ativo: {
        type: DataTypes.BOOLEAN,
        defaultValue: true
    },
    role: {
        type: DataTypes.ENUM('admin', 'perito', 'usuario'),
        defaultValue: 'perito'
    }
}, {
    hooks: {
        beforeCreate: async (user) => {
            if (user.senha) {
                const salt = await bcrypt.genSalt(10);
                user.senha = await bcrypt.hash(user.senha, salt);
            }
        },
        beforeUpdate: async (user) => {
            if (user.changed('senha')) {
                const salt = await bcrypt.genSalt(10);
                user.senha = await bcrypt.hash(user.senha, salt);
            }
        }
    }
});

User.prototype.validarSenha = async function(senha) {
    return await bcrypt.compare(senha, this.senha);
};

module.exports = User;
