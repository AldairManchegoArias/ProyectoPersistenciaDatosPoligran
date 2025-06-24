CREATE DATABASE IF NOT EXISTS PersisDatos;
USE PersisDatos;

CREATE TABLE Departamentos (
    Depto_ID INT AUTO_INCREMENT PRIMARY KEY,
    Depto_Nombre VARCHAR(100)
);

CREATE TABLE Cargos (
    Cargo_ID INT AUTO_INCREMENT PRIMARY KEY,
    Cargo_Nombre VARCHAR(100)
);

CREATE TABLE Empleados (
    Emp_ID INT AUTO_INCREMENT PRIMARY KEY,
    Emp_Nombre VARCHAR(100),
    Emp_Apellidos VARCHAR(100),
    Emp_Correo VARCHAR(100),
    Emp_Fecha_Nacimiento DATE,
    Emp_Sueldo DECIMAL(10, 2),
    Emp_Comision DECIMAL(10, 2),
    Emp_Fecha_Ingreso DATE,
    Emp_Fecha_Salida DATE,
    Emp_Cargo_ID INT,
    Emp_Gerente_ID INT,
    Emp_Depto_ID INT,
    Emp_Estado ENUM('Activo', 'Inactivo') DEFAULT 'Activo',
    FOREIGN KEY (Emp_Cargo_ID) REFERENCES Cargos(Cargo_ID),
    FOREIGN KEY (Emp_Gerente_ID) REFERENCES Empleados(Emp_ID),
    FOREIGN KEY (Emp_Depto_ID) REFERENCES Departamentos(Depto_ID)
);

CREATE TABLE Historico (
    Hist_ID INT AUTO_INCREMENT PRIMARY KEY,
    Emp_ID INT,
    Emp_Hist_Fecha_Registro DATE,
    Emp_Hist_Cargo_ID INT,
    Emp_Hist_Depto_ID INT,
    FOREIGN KEY (Emp_ID) REFERENCES Empleados(Emp_ID),
    FOREIGN KEY (Emp_Hist_Cargo_ID) REFERENCES Cargos(Cargo_ID),
    FOREIGN KEY (Emp_Hist_Depto_ID) REFERENCES Departamentos(Depto_ID)
);
