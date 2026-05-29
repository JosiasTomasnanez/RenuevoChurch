import FontAwesome from '@expo/vector-icons/FontAwesome';
import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { useFonts } from 'expo-font';
import { Stack } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect, useState } from 'react';
import { Alert, Platform, StyleSheet } from 'react-native';
import 'react-native-reanimated';

import * as Application from 'expo-application';
import * as IntentLauncher from 'expo-intent-launcher';

import ExpoFileSystem from 'expo-file-system';
const FileSystem: any = ExpoFileSystem;

import { ApiClient } from '../api/api_client';
import { useColorScheme } from '@/components/useColorScheme';

export {
  ErrorBoundary,
} from 'expo-router';

export const unstable_settings = {
  initialRouteName: '(tabs)',
};

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [loaded, error] = useFonts({
    SpaceMono: require('../assets/fonts/SpaceMono-Regular.ttf'),
    ...FontAwesome.font,
  });

  useEffect(() => {
    if (error) throw error;
  }, [error]);

  useEffect(() => {
    if (loaded) {
      SplashScreen.hideAsync();
    }
  }, [loaded]);

  if (!loaded) {
    return null;
  }

  return (
    <ThemeProvider value={useColorScheme() === 'dark' ? DarkTheme : DefaultTheme}>
      <RootLayoutNav />
    </ThemeProvider>
  );
}

function RootLayoutNav() {
  useEffect(() => {
    if (Platform.OS === 'android') {
      ejecutarChequeoDeVersion();
    }
  }, []);

  const ejecutarChequeoDeVersion = async () => {
    try {
      const versionActual = Application.nativeApplicationVersion;
      const datosServidor = await ApiClient.checkMobileVersion();
      if (!datosServidor) return;

      const { latestVersion, downloadUrl } = datosServidor;

      if (versionActual !== latestVersion && downloadUrl) {
        Alert.alert(
          '¡Nueva versión disponible!',
          `Hay una actualización disponible (v${latestVersion}). ¿Querés instalarla ahora para tener las últimas mejoras?`,
          [
            { text: 'Más tarde', style: 'cancel' },
            { text: 'Actualizar', onPress: () => descargarEInstalarApk(downloadUrl) },
          ]
        );
      }
    } catch (err) {
      console.error('Error en el flujo de verificación de velocidad móvil:', err);
    }
  };

  const descargarEInstalarApk = async (urlDeGitHub: string) => {
    try {
      Alert.alert('Descargando', 'La actualización se está bajando desde GitHub, aguarda un momento...');
      const nombreArchivo = 'renuevo_update.apk';
      const rutaDestino = `${FileSystem.cacheDirectory}${nombreArchivo}`;
      const resultadoDescarga = await FileSystem.downloadAsync(urlDeGitHub, rutaDestino);

      if (resultadoDescarga.status === 200) {
        const contentUri = await FileSystem.getContentUriAsync(resultadoDescarga.uri);
        await IntentLauncher.startActivityAsync('android.intent.action.INSTALL_PACKAGE', {
          data: contentUri,
          flags: 1,
          type: 'application/vnd.android.package-archive',
        });
      } else {
        Alert.alert('Error de descarga', 'No se pudo obtener el archivo desde GitHub.');
      }
    } catch (error) {
      console.error('Error al intentar instalar el APK:', error);
      Alert.alert('Error de installation', 'Hubo un problema al instalar.');
    }
  };

  return (
    <Stack>
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen name="modal" options={{ presentation: 'modal' }} />
    </Stack>
  );
}
