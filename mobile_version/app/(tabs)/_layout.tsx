import React from 'react';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import { Tabs } from 'expo-router';

import Colors from '@/constants/Colors';
import { useColorScheme } from '@/components/useColorScheme';
import { useClientOnlyValue } from '@/components/useClientOnlyValue';

function TabBarIcon(props: {
  name: React.ComponentProps<typeof FontAwesome>['name'];
  color: string;
}) {
  return <FontAwesome size={24} style={{ marginBottom: -3 }} {...props} />;
}

export default function TabLayout() {
  const colorScheme = useColorScheme();

  return (
    <Tabs
      screenOptions={{
        // Tu morado institucional para lo activo, gris suave para lo inactivo
        tabBarActiveTintColor: '#7A4A97',
        tabBarInactiveTintColor: '#888888',
        headerShown: useClientOnlyValue(false, true),
        headerStyle: {
          backgroundColor: '#FFF',
        },
        headerTitleStyle: {
          fontWeight: 'bold',
          color: '#7A4A97',
        },
      }}>
      
      {/* 🔍 PESTAÑA 1: BUSCADOR / LISTADO */}
      <Tabs.Screen
        name="index"
        options={{
          title: 'Buscar',
          headerTitle: '⛪ Renuevo — Personas',
          tabBarIcon: ({ color }) => <TabBarIcon name="search" color={color} />,
        }}
      />
      
      {/* ➕ PESTAÑA 2: AGREGAR PERSONA */}
      <Tabs.Screen
        name="add"
        options={{
          title: 'Agregar',
          headerTitle: '⛪ Alta de Persona',
          tabBarIcon: ({ color }) => <TabBarIcon name="user-plus" color={color} />,
        }}
      />

      {/* ⚙️ PESTAÑA 3: CONFIGURACIÓN (Ministerios, Áreas, CDB, etc.) */}
      <Tabs.Screen
        name="config"
        options={{
          title: 'Config',
          headerTitle: '⚙️ Panel de Control',
          tabBarIcon: ({ color }) => <TabBarIcon name="cogs" color={color} />,
        }}
      />
    </Tabs>
  );
}
