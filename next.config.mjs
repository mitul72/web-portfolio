/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack(config, { isServer }) {
    config.module.rules.push(
      {
        test: /\.glb$/,
        use: {
          loader: "file-loader",
          options: {
            publicPath: "/_next/static/files",
            outputPath: "static/files",
            name: "[name].[hash].[ext]",
          },
        },
      },
      {
        test: /\.(mp3)$/,
        use: [
          {
            loader: "file-loader",
            options: {
              publicPath: `/_next/static/audio/`,
              outputPath: "static/audio/",
              name: "[name].[ext]",
            },
          },
        ],
      }
    );

    return config;
  },
};

export default nextConfig;
